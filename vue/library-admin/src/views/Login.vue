<template>
  <div class="login-page">
    <div class="login-box">
      <el-card shadow="hover">
        <div class="title">图书馆预约管理系统</div>

        <el-form
          :model="form"
          label-width="60px"
          style="margin-top: 20px"
        >
          <el-form-item label="账号">
            <el-input
              v-model="form.username"
              placeholder="请输入管理员账号"
              size="large"
            />
          </el-form-item>

          <el-form-item label="密码">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              style="width: 100%"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const form = reactive({
  username: '',
  password: ''
})

const handleLogin = () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }

  localStorage.setItem('isLogin', 'true')
  ElMessage.success('登录成功')
  router.push('/admin')
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-box {
  width: 380px;
}

.title {
  font-size: 22px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 10px;
  color: #333;
}
</style>