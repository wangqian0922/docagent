<template>
  <div class="chat-container">
    <div class="messages" ref="messagesRef">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="content">
          <div v-if="msg.isStreaming" class="typing-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
          <pre v-if="msg.content">{{ msg.content }}</pre>
          <span v-else-if="msg.isStreaming" class="waiting-text">正在思考...</span>
        </div>
      </div>
    </div>
    
    <div class="input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="2"
        placeholder="请输入问题，按 Ctrl+Enter 发送..."
        @keydown.enter.ctrl="sendMessage"
        :disabled="isLoading"
      />
      <el-button 
        type="primary" 
        @click="sendMessage"
        :loading="isLoading"
        :icon="Promotion"
      >
        发送
      </el-button>
      <el-button 
        @click="undo"
        :disabled="isLoading || messages.length <= 1"
        title="撤销上轮对话"
      >
        撤销
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Promotion } from '@element-plus/icons-vue'
import { chatStream, undoHistory } from '../api'

const messages = ref([
  { role: 'assistant', content: '你好！我是 DocAgent。请先在左侧上传文档，然后我可以帮你回答关于文档的问题。我还可以帮你计算数学题和查询时间。' }
])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesRef = ref(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  
  messages.value.push({ role: 'user', content: userMessage })
  messages.value.push({ role: 'assistant', content: '', isStreaming: true })
  
  isLoading.value = true
  scrollToBottom()
  
  try {
    await chatStream(
      userMessage,
      true,
      (content) => {
        messages.value[messages.value.length - 1].content += content
        scrollToBottom()
      },
      (error) => {
        ElMessage.error(error)
      }
    )
  } catch (error) {
    ElMessage.error('请求失败: ' + error.message)
  } finally {
    messages.value[messages.value.length - 1].isStreaming = false
    isLoading.value = false
    scrollToBottom()
  }
}

const undo = async () => {
  if (messages.value.length < 2) return
  
  try {
    const res = await undoHistory()
    if (res.data.success) {
      messages.value = messages.value.slice(0, -2)
      ElMessage.success('已撤销')
    } else {
      ElMessage.warning(res.data.message)
    }
  } catch (error) {
    ElMessage.error('撤销失败')
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
  margin: 0 10px;
  font-size: 20px;
}

.content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  background: #f0f2f5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message.user .content {
  background: #1890ff;
  color: white;
}

.input-area {
  display: flex;
  padding: 20px;
  border-top: 1px solid #eee;
  gap: 10px;
}

.input-area .el-textarea {
  flex: 1;
}

.typing-indicator {
  display: inline-flex;
  margin-right: 8px;
}

.dot {
  width: 6px;
  height: 6px;
  background: #999;
  border-radius: 50%;
  margin: 0 2px;
  animation: bounce 1.4s infinite ease-in-out;
}

.message.user .dot {
  background: rgba(255,255,255,0.7);
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}

.waiting-text {
  color: #999;
}

pre {
  margin: 0;
  font-family: inherit;
  white-space: pre-wrap;
}
</style>
