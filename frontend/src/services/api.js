import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Legacy endpoint for backward compatibility
export const rankResume = async (resumeFile, jobDescription, jobId = null) => {
  const formData = new FormData()
  formData.append('resume', resumeFile)
  formData.append('job_description', jobDescription)
  if (jobId) {
    formData.append('job_id', jobId)
  }

  const response = await api.post('/rank_resume', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

// New enhanced endpoint with job title
export const analyzeResume = async (resumeFile, jobTitle, jobDescription = null) => {
  const formData = new FormData()
  formData.append('resume', resumeFile)
  formData.append('job_title', jobTitle)
  if (jobDescription) {
    formData.append('job_description', jobDescription)
  }

  const response = await api.post('/analyze_resume', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const getHealth = async () => {
  const response = await api.get('/health')
  return response.data
}

export const getAnalyses = async (jobId, limit = 10) => {
  const response = await api.get(`/analyses/${jobId}`, {
    params: { limit },
  })
  return response.data
}

export const getTopCandidates = async (jobId, limit = 5) => {
  const response = await api.get(`/top_candidates/${jobId}`, {
    params: { limit },
  })
  return response.data
}

// New endpoints
export const getRankings = async (jobTitle = null, limit = 100) => {
  const response = await api.get('/rankings', {
    params: { job_title: jobTitle, limit },
  })
  return response.data
}

export const getHistory = async (limit = 100) => {
  const response = await api.get('/history', {
    params: { limit },
  })
  return response.data
}

export const getTopPerformers = async (limit = 3) => {
  const response = await api.get('/top_performers', {
    params: { limit },
  })
  return response.data
}

export const updateRemarks = async (candidateId, remarks) => {
  const formData = new FormData()
  formData.append('remarks', remarks)

  const response = await api.patch(`/remarks/${candidateId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const deleteCandidate = async (candidateId) => {
  const response = await api.delete(`/candidate/${candidateId}`)
  return response.data
}

export const getCandidate = async (candidateId) => {
  const response = await api.get(`/candidate/${candidateId}`)
  return response.data
}

export const getStatistics = async (jobTitle = null) => {
  const response = await api.get('/statistics', {
    params: { job_title: jobTitle },
  })
  return response.data
}

export default api
