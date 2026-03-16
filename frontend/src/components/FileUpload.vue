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
      accept=".pdf,.txt,.docx"
      drag
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处，或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 PDF、TXT、DOCX 文件
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
    
    <div v-if="taskId" class="task-status">
      <el-alert
        :title="taskStatusText"
        :type="taskStatusType"
        :closable="false"
        show-icon
      />
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadDocument, getTaskStatus } from '../api'

const props = defineProps({
  knowledgeBaseId: {
    type: String,
    default: 'default'
  }
})

const emit = defineEmits(['uploaded'])

const uploadRef = ref(null)
const uploading = ref(false)
const progress = ref(0)
const progressStatus = ref('')
const currentFile = ref(null)
const taskId = ref(null)
const taskStatus = ref('')

const taskStatusText = computed(() => {
  if (taskStatus.value === 'success') return '文档处理完成'
  if (taskStatus.value === 'failed') return '文档处理失败'
  if (taskStatus.value === 'processing') return '正在处理文档...'
  return '等待处理...'
})

const taskStatusType = computed(() => {
  if (taskStatus.value === 'success') return 'success'
  if (taskStatus.value === 'failed') return 'error'
  return 'info'
})

const handleChange = (file) => {
  currentFile.value = file.raw
  taskId.value = null
  taskStatus.value = ''
}

const checkTaskStatus = async () => {
  if (!taskId.value) return
  
  try {
    const res = await getTaskStatus(taskId.value)
    taskStatus.value = res.data.status
    
    if (res.data.status === 'success') {
      progress.value = 100
      progressStatus.value = 'success'
      ElMessage.success('文档上传并处理完成')
      emit('uploaded')
      setTimeout(() => {
        uploadRef.value?.clearFiles()
        currentFile.value = null
        taskId.value = null
        taskStatus.value = ''
      }, 2000)
    } else if (res.data.status === 'failed') {
      progressStatus.value = 'exception'
      ElMessage.error(res.data.error || '处理失败')
    } else if (res.data.status === 'processing') {
      progress.value = res.data.meta?.progress || 50
      setTimeout(checkTaskStatus, 2000)
    }
  } catch (e) {
    console.error(e)
  }
}

const submitUpload = async () => {
  if (!currentFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  uploading.value = true
  progress.value = 0
  progressStatus.value = ''
  taskStatus.value = ''
  
  const formData = new FormData()
  formData.append('file', currentFile.value)
  
  try {
    const res = await uploadDocument(formData, (event) => {
      progress.value = Math.round((event.loaded / event.total) * 100)
    }, props.knowledgeBaseId)
    
    if (res.data.success) {
      progressStatus.value = 'success'
      taskId.value = res.data.file_id
      taskStatus.value = 'processing'
      ElMessage.success(res.data.message)
      setTimeout(checkTaskStatus, 1000)
    }
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

.task-status {
  margin-top: 15px;
}
</style>
