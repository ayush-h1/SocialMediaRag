import React, { useEffect, useState } from 'react'
import ResultCard from '../components/ResultCard.jsx'
import { apiSearch, apiMe } from '../services/api'

export default function Search(){
  const [q, setQ] = useState('rag basics')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [user, setUser] = useState(null)

  useEffect(()=>{
    (async ()=>{
      try{
        const me = await apiMe()
        setUser(me.username)
      }catch{ /* ignore */ }
    })()
  },[])

  const run = async ()=>{
    setLoading(true); setError('')
    try{
      const res = await apiSearch(q)
      setData(res)
    }catch(e){
      setError(e?.response?.data?.detail || e.message || 'Search failed')
    }finally{
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Search</h2>
      {user ? <div className="muted">Signed in as <b>{user}</b></div> : <div className="muted">Not signed in</div>}
      <div className="row" style={{marginTop:10}}>
        <input style={{flex:1}} value={q} onChange={(e)=>setQ(e.target.value)} placeholder="Type your query..." />
        <button onClick={run} disabled={loading}>{loading ? 'Searching…' : 'Search'}</button>
      </div>

      {error && <div className="error" style={{marginTop:10}}>⚠ {error}</div>}

      {data && (
        <div style={{marginTop:16}}>
          <div className="muted">Query: <b>{data.query}</b></div>

          <h3 style={{marginTop:12}}>RAG (local corpus)</h3>
          <div className="grid">
            {data.rag?.map((d,idx)=>(
              <ResultCard key={'rag-'+idx} item={{...d, source:'rag'}} />
            ))}
          </div>

          <h3 style={{marginTop:18}}>Social Sources</h3>
          {data.sources?.map((src, i)=>(
            <div key={'src-'+i} style={{marginTop:10}}>
              <div className="muted">Source: <b>{src.source}</b> {src.note ? `— ${src.note}` : ''}</div>
              <div className="grid">
                {src.items?.map((d,idx)=>(
                  <ResultCard key={'s-'+i+'-'+idx} item={{...d, source:src.source}} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
