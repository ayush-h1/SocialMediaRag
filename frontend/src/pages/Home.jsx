import React from 'react'
import { Link } from 'react-router-dom'

export default function Home(){
  return (
    <div className="card">
      <h2>Welcome 👋</h2>
      <p className="muted">This is a lightweight SocialMediaRAG demo. Use the Search page to query YouTube, Reddit and a tiny RAG corpus.</p>
      <p><Link to="/search">Go to Search →</Link></p>
    </div>
  )
}
