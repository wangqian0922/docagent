<template>
  <div class="app-container">
    <header class="app-header">
      <h1>DocAgent</h1>
      <p>智能文档问答助手</p>
    </header>
    
    <main class="app-main">
      <div class="sidebar">
        <FileUpload @uploaded="onDocumentUploaded" />
        <div class="doc-info">
          <el-card>
            <template #header>
              <span>文档信息</span>
            </template>
            <p>文档数量: {{ docCount }}</p>
          </el-card>
        </div>
      </div>
      
      <div class="chat-area">
        <ChatWindow />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import FileUpload from './components/FileUpload.vue'
import ChatWindow from './components/ChatWindow.vue'
import axios from 'axios'

const docCount = ref(0)

const fetchDocCount = async () => {
  try {
    const res = await axios.get('/api/documents')
    docCount.value = res.data.document_count || 0
  } catch (e) {
    console.error(e)
  }
}

const onDocumentUploaded = () => {
  fetchDocCount()
}

onMounted(() => {
  fetchDocCount()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f7fa;
  min-height: 100vh;
}

.app-container {
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 30px;
  text-align: center;
}

.app-header h1 {
  font-size: 28px;
  margin-bottom: 5px;
}

.app-header p {
  font-size: 14px;
  opacity: 0.9;
}

.app-main {
  flex: 1;
  display: flex;
  padding: 20px;
  gap: 20px;
}

.sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chat-area {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.doc-info p {
  font-size: 14px;
  color: #666;
}
</style>
