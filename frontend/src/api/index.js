import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export const uploadDocument = (formData, onUploadProgress) => {
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  })
}

export const chatStream = async (message, onMessage, onError) => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
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

export const getDocuments = () => api.get('/documents')

export default api
