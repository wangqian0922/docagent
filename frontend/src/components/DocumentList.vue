<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>已上传文档</span>
        <el-button text bg @click="fetchDocuments" :icon="Refresh" />
      </div>
    </template>
    
    <div v-if="documents.length === 0" class="empty">
      暂无上传的文档
    </div>
    
    <div v-else class="document-list">
      <div 
        v-for="doc in documents" 
        :key="doc.file_id" 
        class="document-item"
      >
        <div class="doc-info">
          <el-icon><Document /></el-icon>
          <span class="doc-name" :title="doc.file_name">{{ doc.file_name }}</span>
        </div>
        <div class="doc-meta">
          <span class="chunks">{{ doc.chunks }} 个片段</span>
          <el-button 
            type="danger" 
            size="small" 
            text
            @click="handleDelete(doc.file_id)"
            :icon="Delete"
          />
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Delete, Refresh } from '@element-plus/icons-vue'
import { getDocuments, deleteDocument } from '../api'

const emit = defineEmits(['deleted'])

const documents = ref([])

const fetchDocuments = async () => {
  try {
    const res = await getDocuments()
    documents.value = res.data.documents || []
  } catch (e) {
    console.error(e)
  }
}

const handleDelete = async (fileId) => {
  try {
    await ElMessageBox.confirm('确定要删除此文档吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const res = await deleteDocument(fileId)
    if (res.data.success) {
      ElMessage.success('删除成功')
      fetchDocuments()
      emit('deleted')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

defineExpose({ fetchDocuments })

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty {
  color: #999;
  text-align: center;
  padding: 20px 0;
  font-size: 14px;
}

.document-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.document-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-radius: 6px;
  background: #f5f7fa;
}

.document-item:hover {
  background: #ecf5ff;
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.doc-info .el-icon {
  color: #409eff;
  flex-shrink: 0;
}

.doc-name {
  font-size: 13px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.chunks {
  font-size: 12px;
  color: #999;
}
</style>
