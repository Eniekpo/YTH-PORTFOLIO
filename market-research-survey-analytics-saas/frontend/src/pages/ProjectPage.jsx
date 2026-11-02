import React,{useEffect,useState}from'react';
import{Activity,Download,FileSpreadsheet,Lightbulb,RefreshCcw,UploadCloud,Users,Variable}from'lucide-react';
import{Bar,BarChart,CartesianGrid,ResponsiveContainer,Tooltip,XAxis,YAxis}from'recharts';
import{api,download}from'../api';

const Card=({label,value,sub,icon:Icon})=><div className="metric"><div className="metric-icon">{Icon&&<Icon size={19}/>}</div><div><span>{label}</span><strong>{value}</strong>{sub&&<small>{sub}</small>}</div></div>;

export default function ProjectPage({project}){
  const[datasets,setDatasets]=useState([]);
  const[selected,setSelected]=useState(null);
  const[overview,setOverview]=useState(null);
  const[insights,setInsights]=useState(null);
  const[freq,setFreq]=useState([]);
  const[freqCol,setFreqCol]=useState('');
  const[row,setRow]=useState('');
  const[col,setCol]=useState('');
  const[cross,setCross]=useState(null);
  const[busy,setBusy]=useState(false);
  const[err,setErr]=useState('');

  const loadDatasets=async()=>{
    const d=await api(`/api/projects/${project.id}/datasets`);
    setDatasets(d);setSelected(d[0]||null);
  };
  useEffect(()=>{loadDatasets()},[project.id]);
  useEffect(()=>{if(selected)loadAnalysis()},[selected?.id]);

  const loadAnalysis=async()=>{
    setBusy(true);setErr('');
    try{
      const[o,i]=await Promise.all([
        api(`/api/analysis/${selected.id}/overview`),
        api(`/api/analysis/${selected.id}/insights`)
      ]);
      setOverview(o);setInsights(i);
      const first=o.categorical_columns[0]||o.numeric_columns[0]||'';
      setFreqCol(first);
      if(first)setFreq(await api(`/api/analysis/${selected.id}/frequency?column=${encodeURIComponent(first)}`));
      const cats=o.categorical_columns;
      setRow(cats[0]||'');setCol(cats[1]||'');setCross(null);
    }catch(e){setErr(e.message)}finally{setBusy(false)}
  };

  const upload=async e=>{
    const f=e.target.files[0];if(!f)return;setBusy(true);setErr('');
    const fd=new FormData();fd.append('file',f);
    try{
      const d=await api(`/api/projects/${project.id}/datasets`,{method:'POST',body:fd});
      setDatasets([d,...datasets]);setSelected(d);
    }catch(e){setErr(e.message)}finally{setBusy(false);e.target.value=''}
  };

  const changeFreq=async v=>{
    setFreqCol(v);
    setFreq(await api(`/api/analysis/${selected.id}/frequency?column=${encodeURIComponent(v)}`));
  };
  const runCross=async()=>{
    if(!row||!col)return;
    setCross(await api(`/api/analysis/${selected.id}/crosstab?row=${encodeURIComponent(row)}&col=${encodeURIComponent(col)}`));
  };

  return <>
    <header className="topbar">
      <div><span className="eyebrow">Research project</span><h1>{project.name}</h1><p>{project.research_objective||project.description||'Survey analytics workspace'}</p></div>
      <label className="primary upload"><UploadCloud size={17}/>{busy?'Working...':'Upload responses'}<input type="file" accept=".csv,.xlsx,.xls" onChange={upload}/></label>
    </header>
    {err&&<div className="error page-error">{err}</div>}

    {!selected?<div className="upload-empty"><UploadCloud size={50}/><h2>Upload your survey dataset</h2><p>CSV and Excel files are supported. Try the included demo dataset in the project data folder.</p><label className="primary upload">Choose dataset<input type="file" accept=".csv,.xlsx,.xls" onChange={upload}/></label></div>:
    <>
      <div className="dataset-strip">
        <div><span>Active dataset</span><select value={selected.id} onChange={e=>setSelected(datasets.find(x=>x.id===Number(e.target.value)))}>{datasets.map(d=><option key={d.id} value={d.id}>{d.original_filename}</option>)}</select></div>
        <div className="strip-actions">
          <button className="ghost" onClick={loadAnalysis}><RefreshCcw size={16}/>Refresh</button>
          <button className="ghost" onClick={()=>download(`/api/reports/${selected.id}/xlsx`,'survey_analysis.xlsx')}><FileSpreadsheet size={16}/>Excel</button>
          <button className="ghost" onClick={()=>download(`/api/reports/${selected.id}/pdf`,'survey_analysis_report.pdf')}><Download size={16}/>PDF</button>
        </div>
      </div>

      {overview&&<>
        <section className="metrics">
          <Card label="Responses" value={overview.rows.toLocaleString()} icon={Users}/>
          <Card label="Variables" value={overview.columns} icon={Variable}/>
          <Card label="Completeness" value={`${overview.completeness_pct}%`} icon={Activity}/>
          <Card label="Missing cells" value={overview.missing_cells.toLocaleString()} icon={FileSpreadsheet}/>
        </section>

        <section className="grid two">
          <article className="panel">
            <div className="panel-head"><div><span className="eyebrow">Distribution</span><h3>Response profile</h3></div>
              <select value={freqCol} onChange={e=>changeFreq(e.target.value)}>{[...overview.categorical_columns,...overview.numeric_columns].map(c=><option key={c}>{c}</option>)}</select>
            </div>
            <div className="chart"><ResponsiveContainer width="100%" height={300}><BarChart data={freq} layout="vertical" margin={{left:20,right:25}}><CartesianGrid strokeDasharray="3 3" horizontal={false}/><XAxis type="number"/><YAxis dataKey="value" type="category" width={110} tick={{fontSize:11}}/><Tooltip/><Bar dataKey="count" fill="#4f46e5" radius={[0,7,7,0]}/></BarChart></ResponsiveContainer></div>
          </article>

          <article className="panel insight">
            <div className="panel-head"><div><span className="eyebrow">Automated narrative</span><h3><Lightbulb size={18}/>Research snapshot</h3></div></div>
            <ul>{insights?.bullets?.map((b,i)=><li key={i}>{b}</li>)}</ul>
            <p className="note">{insights?.note}</p>
          </article>
        </section>

        <section className="panel">
          <div className="panel-head">
            <div><span className="eyebrow">Statistical analysis</span><h3>Cross-tabulation & association test</h3></div>
            <div className="inline">
              <select value={row} onChange={e=>setRow(e.target.value)}>{overview.categorical_columns.map(c=><option key={c}>{c}</option>)}</select>
              <span>×</span>
              <select value={col} onChange={e=>setCol(e.target.value)}>{overview.categorical_columns.map(c=><option key={c}>{c}</option>)}</select>
              <button className="primary" onClick={runCross}>Run analysis</button>
            </div>
          </div>
          {cross?<div className="cross-wrap">
            <div className="test-stat"><b>Chi-square:</b> {cross.chi_square??'n/a'} <b>p-value:</b> {cross.p_value??'n/a'} <b>df:</b> {cross.degrees_of_freedom??'n/a'}</div>
            <table><thead><tr><th>{cross.row_variable}</th>{cross.columns.map(c=><th key={c}>{c}</th>)}</tr></thead>
            <tbody>{cross.rows.map(r=><tr key={r.label}><th>{r.label}</th>{r.counts.map((v,i)=><td key={i}><b>{v}</b><span>{r.row_pct[i]}%</span></td>)}</tr>)}</tbody></table>
          </div>:<div className="placeholder">Choose two categorical variables and run the analysis to produce a contingency table and chi-square test.</div>}
        </section>

        <section className="panel">
          <div className="panel-head"><div><span className="eyebrow">Data quality</span><h3>Variable profile</h3></div></div>
          <div className="table-scroll"><table><thead><tr><th>Variable</th><th>Type</th><th>Unique</th><th>Missing</th><th>Missing %</th></tr></thead>
          <tbody>{overview.profile.map(x=><tr key={x.column}><td><b>{x.column}</b></td><td>{x.dtype}</td><td>{x.unique}</td><td>{x.missing}</td><td>{x.missing_pct}%</td></tr>)}</tbody></table></div>
        </section>
      </>}
    </>}
  </>
}
