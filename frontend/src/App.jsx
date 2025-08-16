import React from 'react'
import { Routes, Route, Link, Navigate } from 'react-router-dom'
import Home from './pages/Home.jsx'
import Search from './pages/Search.jsx'
import Login from './pages/Login.jsx'

const Header = () => (
  <header>
    <div className="container" style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
      <div className="brand">SocialMediaRAG</div>
      <nav style={{display:'flex',gap:14}}>
        <Link to="/">Home</Link>
        <Link to="/search">Search</Link>
        <Link to="/login">Login</Link>
      </nav>
    </div>
  </header>
)

const Footer = () => (
  <footer>
    <div className="container">© {new Date().getFullYear()} SocialMediaRAG — demo build</div>
  </footer>
)

export default function App(){
  return (
    <>
      <Header/>
      <div className="container">
        <Routes>
          <Route path="/" element={<Home/>} />
          <Route path="/search" element={<Search/>} />
          <Route path="/login" element={<Login/>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
      <Footer/>
    </>
  )
}
