import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

// attach token
api.interceptors.request.use((cfg)=>{
  const t = localStorage.getItem('token')
  if (t) cfg.headers['Authorization'] = `Bearer ${t}`
  return cfg
})

export async function apiSearch(q){
  const { data } = await api.get('/search', { params: { q } })
  return data
}

export async function apiLogin(username, password){
  const { data } = await api.post('/auth/login', { username, password })
  return data
}

export async function apiMe(){
  const { data } = await api.get('/auth/me')
  return data
}
