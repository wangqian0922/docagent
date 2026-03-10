<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>上传文档</span>
      </div>
    </template>
    
    <el-upload
      ref="uploadRef"
      :auto-upload="false"
      :on-change="handleChange"
      :on-success="handleSuccess"
      :on-error="handleError"
      :limit="1"
      accept=".pdf,.txt"
      drag
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处，或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 PDF 和 TXT 文件
        </div>
      </template>
    </el-upload>
    
    <div class="upload-actions">
      <el-button type="primary" @click="submitUpload" :loading="uploading">
        上传
      </el-button>
    </div>
    
    <el-progress
      v-if="uploading"
      :percentage="progress"
      :status="progressStatus"
    />
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadDocument } from '../api'

const emit = defineEmits(['uploaded'])

const uploadRef = ref(null)
const uploading = ref(false)
const progress = ref(0)
const progressStatus = ref('')
const currentFile = ref(null)

const handleChange = (file) => {
  currentFile.value = file.raw
}

const submitUpload = async () => {
  if (!currentFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  uploading.value = true
  progress.value = 0
  progressStatus.value = ''
  
  const formData = new FormData()
  formData.append('file', currentFile.value)
  
  try {
    const res = await uploadDocument(formData, (event) => {
      progress.value = Math.round((event.loaded / event.total) * 100)
    })
    
    progressStatus.value = 'success'
    ElMessage.success(res.data.message)
    emit('uploaded')
    
    setTimeout(() => {
      uploadRef.value?.clearFiles()
      currentFile.value = null
    }, 1000)
  } catch (error) {
    progressStatus.value = 'exception'
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

const handleSuccess = () => {
  ElMessage.success('上传成功')
}

const handleError = () => {
  ElMessage.error('上传失败')
}
</script>

<style scoped>
.card-header {
  font-weight: 600;
}

.upload-actions {
  margin-top: 15px;
  text-align: center;
}

.el-icon--upload {
  font-size: 40px;
  color: #409eff;
  margin-bottom: 10px;
}
</style>
