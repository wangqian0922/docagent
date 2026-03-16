<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>知识库管理</span>
        <el-button text bg @click="showCreateDialog = true" :icon="Plus" />
      </div>
    </template>
    
    <div v-if="knowledgeBases.length === 0" class="empty">
      暂无知识库
    </div>
    
    <div v-else class="kb-list">
      <div 
        v-for="kb in knowledgeBases" 
        :key="kb.id" 
        :class="['kb-item', { active: currentKb === kb.id }]"
        @click="selectKnowledgeBase(kb.id)"
      >
        <div class="kb-info">
          <el-icon><Folder /></el-icon>
          <span class="kb-name">{{ kb.name }}</span>
        </div>
        <div class="kb-meta">
          <span>{{ kb.documents }} 个文档</span>
        </div>
      </div>
    </div>

    <el-dialog v-model="showCreateDialog" title="创建知识库" width="400px">
      <el-input v-model="newKbName" placeholder="请输入知识库名称" />
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createKb" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Folder, Plus } from '@element-plus/icons-vue'
import { getKnowledgeBases, createKnowledgeBase } from '../api'

const emit = defineEmits(['change'])

const knowledgeBases = ref([])
const currentKb = ref('default')
const showCreateDialog = ref(false)
const newKbName = ref('')
const creating = ref(false)

const fetchKnowledgeBases = async () => {
  try {
    const res = await getKnowledgeBases()
    knowledgeBases.value = res.data.knowledge_bases || []
    if (knowledgeBases.value.length > 0 && !currentKb.value) {
      currentKb.value = knowledgeBases.value[0].id
      emit('change', currentKb.value)
    }
  } catch (e) {
    console.error(e)
  }
}

const selectKnowledgeBase = (kbId) => {
  currentKb.value = kbId
  emit('change', kbId)
}

const createKb = async () => {
  if (!newKbName.value.trim()) {
    ElMessage.warning('请输入知识库名称')
    return
  }
  
  creating.value = true
  try {
    await createKnowledgeBase(newKbName.value.trim())
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    newKbName.value = ''
    fetchKnowledgeBases()
  } catch (e) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

defineExpose({ 
  currentKb,
  fetchKnowledgeBases 
})

onMounted(() => {
  fetchKnowledgeBases()
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

.kb-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.kb-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.kb-item:hover {
  background: #f5f7fa;
}

.kb-item.active {
  background: #ecf5ff;
  border: 1px solid #409eff;
}

.kb-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.kb-info .el-icon {
  color: #409eff;
}

.kb-name {
  font-size: 14px;
  color: #333;
}

.kb-meta {
  font-size: 12px;
  color: #999;
}
</style>
