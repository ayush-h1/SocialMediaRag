import React from 'react'

export default function ResultCard({ item }){
  return (
    <div className="card">
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center', marginBottom:8}}>
        <strong>{item.title || item.url || 'Untitled'}</strong>
        {item.source && <span className="badge">{item.source}</span>}
      </div>
      {item.description && <p className="muted">{item.description}</p>}
      {item.url && <p><a href={item.url} target="_blank" rel="noreferrer">Open →</a></p>}
      {typeof item.score === 'number' && <div className="muted">Relevance: {item.score}</div>}
      {(item.channel || item.subreddit || item.author) && (
        <div className="muted">By {item.channel || item.author} {item.subreddit ? `in r/${item.subreddit}` : ''}</div>
      )}
    </div>
  )
}
