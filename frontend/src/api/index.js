import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export const uploadDocument = (formData, onUploadProgress, knowledgeBaseId = 'default') => {
  return api.post(`/upload?knowledge_base_id=${knowledgeBaseId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  })
}

export const getTaskStatus = (taskId) => {
  return api.get(`/task/${taskId}`)
}

export const chatStream = async (message, useHistory = true, onMessage, onError) => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, use_history: useHistory }),
  })

  if (!response.ok) {
    throw new Error('请求失败')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { value, done } = await reader.read()
    if (done) break

    const chunk = decoder.decode(value)
    const lines = chunk.split('\n')

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        if (data === '[DONE]') {
          return
        }
        try {
          const parsed = JSON.parse(data)
          if (parsed.content) {
            onMessage(parsed.content)
          } else if (parsed.error) {
            onError(parsed.error)
          }
        } catch (e) {}
      }
    }
  }
}

export const getHistory = () => api.get('/history')

export const clearHistory = () => api.post('/history/clear')

export const undoHistory = () => api.post('/history/undo')

export const getDocuments = (knowledgeBaseId = 'default') => 
  api.get(`/documents?knowledge_base_id=${knowledgeBaseId}`)

export const deleteDocument = (fileId, knowledgeBaseId = 'default') => 
  api.delete(`/documents/${fileId}?knowledge_base_id=${knowledgeBaseId}`)

export const getKnowledgeBases = () => api.get('/knowledge-bases')

export const createKnowledgeBase = (name) => 
  api.post(`/knowledge-bases?name=${encodeURIComponent(name)}`)

export const getStats = () => api.get('/stats')

export const getAgentLogs = (limit = 50) => api.get(`/agent-logs?limit=${limit}`)

export default api
