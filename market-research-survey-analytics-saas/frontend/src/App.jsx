import React,{useEffect,useState}from'react';
import{BarChart3,Database,FileText,LogOut,PlusCircle}from'lucide-react';
import{api}from'./api';
import AuthPage from'./pages/AuthPage';
import ProjectPage from'./pages/ProjectPage';

export default function App(){
  const[logged,setLogged]=useState(!!localStorage.getItem('if_token'));
  const[projects,setProjects]=useState([]);
  const[selected,setSelected]=useState(null);
  const[showNew,setShowNew]=useState(false);
  const[form,setForm]=useState({name:'',description:'',research_objective:''});

  const logout=()=>{localStorage.removeItem('if_token');localStorage.removeItem('if_user');setLogged(false);setSelected(null)};
  const load=async()=>{try{const p=await api('/api/projects');setProjects(p);if(!selected&&p[0])setSelected(p[0])}catch(e){logout()}};
  useEffect(()=>{if(logged)load()},[logged]);

  const create=async(e)=>{
    e.preventDefault();
    const p=await api('/api/projects',{method:'POST',body:form});
    setProjects([p,...projects]);setSelected(p);setShowNew(false);
    setForm({name:'',description:'',research_objective:''});
  };

  if(!logged)return <AuthPage onLogin={()=>setLogged(true)}/>;

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brandmark"><BarChart3/></div><div><strong>InsightForge</strong><span>Research Analytics</span></div></div>
      <button className="primary full" onClick={()=>setShowNew(true)}><PlusCircle size={17}/>New project</button>
      <div className="nav-label">Research projects</div>
      <div className="project-list">{projects.map(p=><button key={p.id} className={selected?.id===p.id?'project active':'project'} onClick={()=>setSelected(p)}><Database size={16}/><span>{p.name}</span></button>)}</div>
      <div className="sidebar-foot"><div className="user-chip">{localStorage.getItem('if_user')||'Portfolio User'}</div><button className="ghost" onClick={logout}><LogOut size={16}/>Sign out</button></div>
    </aside>
    <main className="main">{selected?<ProjectPage project={selected}/>:<div className="empty"><FileText size={48}/><h2>Create your first research project</h2><p>Upload survey data and turn responses into decision-ready insight.</p></div>}</main>

    {showNew&&<div className="modal-backdrop"><form className="modal" onSubmit={create}>
      <h2>New research project</h2>
      <label>Project name<input required value={form.name} onChange={e=>setForm({...form,name:e.target.value})} placeholder="Customer Experience Study"/></label>
      <label>Description<textarea value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/></label>
      <label>Research objective<textarea value={form.research_objective} onChange={e=>setForm({...form,research_objective:e.target.value})} placeholder="Understand satisfaction drivers and segment differences"/></label>
      <div className="actions"><button type="button" className="ghost" onClick={()=>setShowNew(false)}>Cancel</button><button className="primary">Create project</button></div>
    </form></div>}
  </div>
}
