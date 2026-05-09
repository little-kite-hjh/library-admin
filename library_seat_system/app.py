from flask import request, jsonify
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 1. 初始化 Flask 应用
app = Flask(__name__)
app.config['JSON_AS_ASCLL']=False
# 2. 配置数据库（用 SQLite，不用管MySQL）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_seat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. 初始化 SQLAlchemy，和 Flask 应用绑定
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment="用户名/学号")
    password = db.Column(db.String(100), nullable=False, comment="密码")
    role = db.Column(db.String(10), default="student", comment="角色：student学生 / admin管理员")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<User {self.username}>"

# ---------------------- 2. 座位表 ----------------------
class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_name = db.Column(db.String(50), nullable=False, comment="教室/图书馆名称")
    seat_number = db.Column(db.String(20), nullable=False, comment="座位号，如A01")
    status = db.Column(db.String(10), default="available", comment="状态：available空闲 / reserved已预约 / occupied使用中")
    capacity = db.Column(db.Integer, default=1, comment="座位容量")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

    # 复合唯一约束：同一个教室+座位号不能重复
    __table_args__ = (
        db.UniqueConstraint('room_name', 'seat_number', name='_room_seat_uc'),
    )

    def __repr__(self):
        return f"<Seat {self.room_name}-{self.seat_number}>"

# ---------------------- 3. 预约记录表 ----------------------
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment="预约用户ID")
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'), nullable=False, comment="预约座位ID")
    start_time = db.Column(db.DateTime, nullable=False, comment="预约开始时间")
    end_time = db.Column(db.DateTime, nullable=False, comment="预约结束时间")
    status = db.Column(db.String(10), default="pending", comment="状态：pending待生效 / active使用中 / completed已完成 / cancelled已取消")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="预约创建时间")

    # 外键关联
    user = db.relationship('User', backref=db.backref('reservations', lazy=True))
    seat = db.relationship('Seat', backref=db.backref('reservations', lazy=True))

    def __repr__(self):
        return f"<Reservation {self.user.username} -> {self.seat.room_name}-{self.seat.seat_number}>"

# ---------------------- 初始化数据库 ----------------------
with app.app_context():
    db.create_all()
    # 初始化测试座位数据（防止重复添加）
    if not Seat.query.first():
        seats = [
            Seat(room_name="一楼自习室", seat_number="A01", status="available"),
            Seat(room_name="一楼自习室", seat_number="A02", status="available"),
            Seat(room_name="二楼自习室", seat_number="B01", status="available"),
            Seat(room_name="电子阅览室", seat_number="C01", status="available")
        ]
        db.session.add_all(seats)
        db.session.commit()

# 首页路由
@app.route('/')
def index():
    return "图书馆预约系统运行成功！"
@app.route('/seats', methods=['GET'])
def get_seats():
    # 查询所有空闲座位
    seats = Seat.query.all()
    # 转成列表返回
    result = []
    for seat in seats:
        result.append({
            "id": seat.id,
            "room_name": seat.room_name,
            "seat_number": seat.seat_number,
            "status": seat.status
        })
    return {"code": 200, "data": result}
@app.route('/reserve', methods=['POST'])
def create_reservation():
    data = request.get_json()
    seat_id = data.get('seat_id')
    user_id = data.get('user_id')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    # 基础参数校验
    if not all([seat_id, user_id, start_time_str, end_time_str]):
        return jsonify({"code": 400, "msg": "参数不完整"})

    try:
        # 时间格式转换
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

        # 开启事务+行锁：查询座位并锁定，防止并发预约
        seat = Seat.query.filter_by(id=seat_id, status='available').with_for_update().first()
        if not seat:
            return jsonify({"code": 400, "msg": "座位已被预约或不存在"})

        # 检查时间段是否冲突
        conflict = Reservation.query.filter(
            Reservation.seat_id == seat_id,
            Reservation.status.in_(['pending', 'active']),
            Reservation.start_time < end_time,
            Reservation.end_time > start_time
        ).first()
        if conflict:
            return jsonify({"code": 400, "msg": "该时间段座位已被预约"})

        # 创建预约记录
        new_reservation = Reservation(
            user_id=user_id,
            seat_id=seat_id,
            start_time=start_time,
            end_time=end_time,
            status='pending'
        )
        db.session.add(new_reservation)

        # 更新座位状态
        seat.status = 'reserved'
        db.session.commit()

        return jsonify({
            "code": 200,
            "msg": "预约成功",
            "data": {"reservation_id": new_reservation.id}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": "预约失败：" + str(e)})
@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation or reservation.status == 'cancelled':
        return jsonify({"code": 400, "msg": "预约不存在或已取消"})

    # 更新预约状态和座位状态
    reservation.status = 'cancelled'
    seat = Seat.query.get(reservation.seat_id)
    seat.status = 'available'
    db.session.commit()
@app.route('/my_reservations/<int:user_id>', methods=['GET'])
def my_reservations(user_id):
    # 查询该用户的所有预约，按预约时间倒序排列
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
    result = []
    for r in reservations:
        result.append({
            "reservation_id": r.id,
            "seat_id": r.seat_id,
            "room_name": r.seat.room_name,
            "seat_number": r.seat.seat_number,
            "start_time": r.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": r.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            "status": r.status
        })
    return jsonify({
        "code": 200,
        "msg": "查询成功",
        "data": result
    })
    return jsonify({"code": 200, "msg": "取消预约成功"})
if __name__ == '__main__':
    app.run(debug=True)