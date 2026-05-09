<template>
  <div class="layout-wrap">
    <!-- 左侧侧边栏 -->
    <div class="sidebar">
      <div class="logo-box">📚 图书馆管理系统</div>

      <div 
        class="menu-item"
        :class="{ active: activeMenu === 'home' }"
        @click="activeMenu = 'home'"
      >
        🏠 首页数据
      </div>

      <div 
        class="menu-item"
        :class="{ active: activeMenu === 'book' }"
        @click="activeMenu = 'book'"
      >
        📖 图书管理
      </div>

      <div 
        class="menu-item"
        :class="{ active: activeMenu === 'user' }"
        @click="activeMenu = 'user'"
      >
        👤 用户管理
      </div>

      <div class="menu-item logout-btn" @click="handleLogout">
        🚪 退出登录
      </div>
    </div>

    <!-- 右侧主区域 -->
    <div class="main-wrap">
      <div class="header-top">
        <span class="title-text">后台管理中心</span>
        <span class="admin-text">👋 欢迎管理员</span>
      </div>

      <div class="content-wrap">

        <!-- 首页 -->
        <div v-if="activeMenu === 'home'">
          <div class="page-title">首页统计数据</div>
          <div class="card-row">
            <div class="data-card">
              <div class="num">{{ bookList.length }}</div>
              <div class="desc">总图书数量</div>
            </div>
            <div class="data-card">
              <div class="num">{{ bookList.filter(i=>i.status==='借出').length }}</div>
              <div class="desc">当前借阅中</div>
            </div>
            <div class="data-card">
              <div class="num">{{ userList.length }}</div>
              <div class="desc">注册读者人数</div>
            </div>
          </div>
        </div>

        <!-- 图书管理 -->
        <div v-if="activeMenu === 'book'">
          <div class="page-title">图书管理</div>
          <div class="content-card">
            <div class="card-head">
              <span>图书列表</span>
              <button class="add-btn" @click="openAddBook">+ 新增图书</button>
            </div>

            <div class="table-row head-row">
              <div class="td">序号</div>
              <div class="td">书名</div>
              <div class="td">作者</div>
              <div class="td">状态</div>
              <div class="td">操作</div>
            </div>
            <div class="table-row" v-for="(item, index) in bookList" :key="index">
              <div class="td">{{ index + 1 }}</div>
              <div class="td">{{ item.name }}</div>
              <div class="td">{{ item.author }}</div>
              <div class="td">
                <span class="tag green" v-if="item.status === '在馆'">在馆</span>
                <span class="tag orange" v-else>借出</span>
              </div>
              <div class="td">
                <button class="edit-btn" @click="openEditBook(index)">编辑</button>
                <button class="del-btn" @click="deleteBook(index)">删除</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 用户管理 -->
        <div v-if="activeMenu === 'user'">
          <div class="page-title">读者用户管理</div>
          <div class="content-card">
            <div class="card-head">
              <span>读者列表</span>
              <button class="add-btn" @click="openAddUser">+ 新增读者</button>
            </div>

            <div class="table-row head-row">
              <div class="td">序号</div>
              <div class="td">用户名</div>
              <div class="td">角色</div>
              <div class="td">状态</div>
              <div class="td">操作</div>
            </div>
            <div class="table-row" v-for="(item, index) in userList" :key="index">
              <div class="td">{{ index + 1 }}</div>
              <div class="td">{{ item.username }}</div>
              <div class="td">{{ item.role }}</div>
              <div class="td">
                <span class="tag green" v-if="item.status === '正常'">正常</span>
                <span class="tag red" v-else>禁用</span>
              </div>
              <div class="td">
                <button class="edit-btn" @click="openEditUser(index)">编辑</button>
                <button class="del-btn" @click="deleteUser(index)">删除</button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 图书弹窗 -->
    <div class="modal" v-if="bookDialogVisible" @click="bookDialogVisible=false"></div>
    <div class="dialog" v-if="bookDialogVisible">
      <div class="dialog-header">
        <span>{{ editBookIndex===null ? '新增图书' : '编辑图书' }}</span>
        <button @click="bookDialogVisible=false">×</button>
      </div>
      <div class="dialog-body">
        <div class="form-item">
          <label>书名</label>
          <input v-model="bookForm.name" placeholder="请输入书名" />
        </div>
        <div class="form-item">
          <label>作者</label>
          <input v-model="bookForm.author" placeholder="请输入作者" />
        </div>
        <div class="form-item">
          <label>状态</label>
          <select v-model="bookForm.status">
            <option value="在馆">在馆</option>
            <option value="借出">借出</option>
          </select>
        </div>
      </div>
      <div class="dialog-footer">
        <button @click="bookDialogVisible=false">取消</button>
        <button class="submit" @click="saveBook">确认保存</button>
      </div>
    </div>

    <!-- 用户弹窗 -->
    <div class="modal" v-if="userDialogVisible" @click="userDialogVisible=false"></div>
    <div class="dialog" v-if="userDialogVisible">
      <div class="dialog-header">
        <span>{{ editUserIndex===null ? '新增读者' : '编辑读者' }}</span>
        <button @click="userDialogVisible=false">×</button>
      </div>
      <div class="dialog-body">
        <div class="form-item">
          <label>用户名</label>
          <input v-model="userForm.username" placeholder="请输入用户名" />
        </div>
        <div class="form-item">
          <label>角色</label>
          <select v-model="userForm.role">
            <option value="管理员">管理员</option>
            <option value="普通读者">普通读者</option>
          </select>
        </div>
        <div class="form-item">
          <label>状态</label>
          <select v-model="userForm.status">
            <option value="正常">正常</option>
            <option value="禁用">禁用</option>
          </select>
        </div>
      </div>
      <div class="dialog-footer">
        <button @click="userDialogVisible=false">取消</button>
        <button class="submit" @click="saveUser">确认保存</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const activeMenu = ref('home')

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('isLogin')
  router.push('/login')
}

// 图书 30000 本
const bookList = ref(Array.from({ length: 30000 }, (_, i) => ({
  name: `图书${i + 1}`,
  author: `作者${i + 1}`,
  status: i % 2 === 0 ? '在馆' : '借出'
})))

const bookDialogVisible = ref(false)
const editBookIndex = ref(null)
const bookForm = ref({ name: '', author: '', status: '在馆' })

const openAddBook = () => {
  editBookIndex.value = null
  bookForm.value = { name: '', author: '', status: '在馆' }
  bookDialogVisible.value = true
}

const openEditBook = (index) => {
  editBookIndex.value = index
  bookForm.value = { ...bookList.value[index] }
  bookDialogVisible.value = true
}

const saveBook = () => {
  if (editBookIndex.value === null) {
    bookList.value.push({ ...bookForm.value })
  } else {
    bookList.value[editBookIndex.value] = { ...bookForm.value }
  }
  bookDialogVisible.value = false
}

const deleteBook = (index) => {
  bookList.value.splice(index, 1)
}

// 读者 5000 人
const userList = ref(Array.from({ length: 5000 }, (_, i) => ({
  username: `读者${i + 1}`,
  role: i < 10 ? '管理员' : '普通读者',
  status: i % 5 === 0 ? '禁用' : '正常'
})))

const userDialogVisible = ref(false)
const editUserIndex = ref(null)
const userForm = ref({ username: '', role: '普通读者', status: '正常' })

const openAddUser = () => {
  editUserIndex.value = null
  userForm.value = { username: '', role: '普通读者', status: '正常' }
  userDialogVisible.value = true
}

const openEditUser = (index) => {
  editUserIndex.value = index
  userForm.value = { ...userList.value[index] }
  userDialogVisible.value = true
}

const saveUser = () => {
  if (editUserIndex.value === null) {
    userList.value.push({ ...userForm.value })
  } else {
    userList.value[editUserIndex.value] = { ...userForm.value }
  }
  userDialogVisible.value = false
}

const deleteUser = (index) => {
  userList.value.splice(index, 1)
}
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }
.layout-wrap { display: flex; height: 100vh; background: #f2f5f9; }

/* 侧边栏 */
.sidebar { width: 220px; background: #1f2937; color: #fff; padding-top: 20px; }
.logo-box { text-align: center; font-size: 18px; padding-bottom: 30px; border-bottom: 1px solid #374151; margin-bottom: 20px; }
.menu-item { padding: 14px 25px; cursor: pointer; transition: all 0.3s; border-left: 4px solid transparent; }
.menu-item:hover { background: #374151; }
.menu-item.active { background: #2563eb; border-left-color: #60a5fa; }
.logout-btn { margin-top: 30px; color: #f87171; }

/* 头部 */
.main-wrap { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.header-top { height: 60px; background: #fff; display: flex; justify-content: space-between; align-items: center; padding: 0 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.title-text { font-size: 17px; font-weight: 600; color: #333; }
.admin-text { color: #666; }

/* 内容 */
.content-wrap { flex: 1; padding: 25px; overflow-y: auto; }
.page-title { font-size: 20px; font-weight: 600; margin-bottom: 20px; color: #333; }

/* 数据卡片 */
.card-row { display: flex; gap: 20px; }
.data-card { flex: 1; background: #fff; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; }
.data-card .num { font-size: 36px; font-weight: bold; color: #2563eb; margin-bottom: 8px; }
.data-card .desc { color: #666; font-size: 15px; }

/* 表格卡片 */
.content-card { background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 20px; }
.card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; font-size: 16px; font-weight: 600; }
.add-btn { background: #2563eb; color: #fff; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; }

.table-row { display: flex; padding: 12px 0; border-bottom: 1px solid #eee; align-items: center; }
.head-row { font-weight: 600; color: #333; }
.td { flex: 1; text-align: center; font-size: 14px; }

.tag { padding: 3px 8px; border-radius: 4px; font-size: 12px; color: #fff; }
.green { background: #10b981; }
.orange { background: #f59e0b; }
.red { background: #ef4444; }

.edit-btn { background: #2563eb; color: #fff; border: none; padding: 4px 8px; border-radius: 3px; margin-right: 5px; cursor: pointer; }
.del-btn { background: #ef4444; color: #fff; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; }

/* 弹窗 */
.modal { position: fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.4); z-index:99; }
.dialog { position: fixed; top:50%; left:50%; transform:translate(-50%,-50%); width:400px; background:#fff; border-radius:8px; z-index:100; }
.dialog-header { padding:15px 20px; background:#f5f7fa; display:flex; justify-content:space-between; font-weight:600; }
.dialog-header button { background:none; border:none; font-size:18px; cursor:pointer; }
.dialog-body { padding:20px; }
.form-item { margin-bottom:15px; }
.form-item label { display:block; margin-bottom:5px; font-size:14px; }
.form-item input, .form-item select { width:100%; padding:8px; border:1px solid #ddd; border-radius:4px; }
.dialog-footer { padding:15px 20px; text-align:right; border-top:1px solid #eee; }
.dialog-footer button { padding:6px 15px; margin-left:10px; border:1px solid #ddd; border-radius:4px; cursor:pointer; }
.submit { background:#2563eb; color:#fff; border:none !important; }
</style>