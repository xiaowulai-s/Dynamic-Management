import request from './request'

// 获取反馈列表
export const getFeedbacks = (params?: {
  skip?: number
  limit?: number
  status?: string
}) => {
  return request.get('/feedback/', { params })
}

// 提交反馈
export const submitFeedback = (data: {
  title: string
  content: string
}) => {
  return request.post('/feedback/', data)
}

// 回复反馈
export const replyFeedback = (id: number, reply: string) => {
  return request.put(`/feedback/${id}/reply`, { reply })
}

// 标记反馈已读
export const markFeedbackRead = (id: number) => {
  return request.put(`/feedback/${id}/read`)
}

// 获取反馈统计
export const getFeedbackStats = () => {
  return request.get('/feedback/stats')
}
