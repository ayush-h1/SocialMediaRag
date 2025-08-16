import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiLogin } from '../services/api'

export default function Login(){
  const [username,setUsername] = useState('')
  const [password,setPassword] = useState('')
  const [error,setError] = useState('')
  const navigate = useNavigate()

  const submit = async (e)=>{
    e.preventDefault()
    setError('')
    try{
      const res = await apiLogin(username, password)
      localStorage.setItem('token', res.access_token)
      navigate('/search')
    }catch(err){
      setError(err?.response?.data?.detail || err.message || 'Login failed')
    }
  }

  return (
    <div className="card">
      <h2>Login</h2>
      <form onSubmit={submit} style={{display:'grid',gap:10,maxWidth:360}}>
        <input placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button type="submit">Sign in</button>
        {error && <div className="error">⚠ {error}</div>}
      </form>
      <p className="muted" style={{marginTop:10}}>Demo login accepts any non-empty username/password.</p>
    </div>
  )
}
