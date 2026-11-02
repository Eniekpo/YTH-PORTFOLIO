import React,{useState}from'react';
import{BarChart3,CheckCircle2}from'lucide-react';
import{api}from'../api';

export default function AuthPage({onLogin}){
  const[mode,setMode]=useState('login');
  const[email,setEmail]=useState('demo@insightforge.dev');
  const[password,setPassword]=useState('portfolio123');
  const[name,setName]=useState('Portfolio Analyst');
  const[err,setErr]=useState('');
  const submit=async e=>{
    e.preventDefault();setErr('');
    try{
      const body=mode==='register'?{email,password,full_name:name}:{email,password};
      const r=await api(`/api/auth/${mode}`,{method:'POST',body});
      localStorage.setItem('if_token',r.access_token);localStorage.setItem('if_user',r.full_name);onLogin();
    }catch(e){setErr(e.message)}
  };
  return <div className="auth">
    <section className="auth-hero">
      <div className="brand big"><div className="brandmark"><BarChart3/></div><div><strong>InsightForge</strong><span>Market Research & Survey Analytics</span></div></div>
      <h1>From raw survey responses to <em>decision-ready insight.</em></h1>
      <p>A full-stack research analytics workspace for data upload, quality profiling, cross-tabulation, statistical testing, automated narratives and report export.</p>
      <div className="hero-points"><span><CheckCircle2/>Survey data workspace</span><span><CheckCircle2/>Cross-tabs + chi-square</span><span><CheckCircle2/>PDF & Excel reporting</span></div>
    </section>
    <section className="auth-card"><form onSubmit={submit}>
      <h2>{mode==='login'?'Welcome back':'Create account'}</h2><p>{mode==='login'?'Use the demo account or register your own.':'Set up a local portfolio account.'}</p>
      {mode==='register'&&<label>Full name<input value={name} onChange={e=>setName(e.target.value)} required/></label>}
      <label>Email<input type="email" value={email} onChange={e=>setEmail(e.target.value)} required/></label>
      <label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} required/></label>
      {err&&<div className="error">{err}</div>}
      <button className="primary full">{mode==='login'?'Sign in':'Register'}</button>
      <button type="button" className="link" onClick={()=>setMode(mode==='login'?'register':'login')}>{mode==='login'?'Create a new account':'Already have an account? Sign in'}</button>
      <div className="demo"><b>Demo credentials</b><code>demo@insightforge.dev</code><code>portfolio123</code></div>
    </form></section>
  </div>
}
