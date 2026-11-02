const BASE=import.meta.env.VITE_API_URL||'http://localhost:8000';
export const token=()=>localStorage.getItem('if_token');
export async function api(path,options={}){
  const headers={...(options.headers||{})};
  if(token())headers.Authorization=`Bearer ${token()}`;
  if(options.body&&!(options.body instanceof FormData)){
    headers['Content-Type']='application/json';
    options.body=JSON.stringify(options.body);
  }
  const r=await fetch(`${BASE}${path}`,{...options,headers});
  if(!r.ok){let m='Request failed';try{const j=await r.json();m=j.detail||m}catch{}throw new Error(m)}
  const ct=r.headers.get('content-type')||'';
  return ct.includes('application/json')?r.json():r.blob();
}
export async function download(path,filename){
  const blob=await api(path);const u=URL.createObjectURL(blob);
  const a=document.createElement('a');a.href=u;a.download=filename;a.click();URL.revokeObjectURL(u);
}
