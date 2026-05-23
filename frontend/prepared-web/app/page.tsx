'use client'

import {FormEvent,useEffect,useState} from 'react'
import {runEvaluation,getReport,getPoints,inviteOrganizationUser} from '../services/api'
import {useJobPolling} from '../hooks/useJobPolling'
import ReportCard from '../components/ReportCard'

function MetricCard({label,value}:{label:string,value:string}){
 return(
  <div style={{border:'1px solid #e5e7eb',borderRadius:'12px',padding:'16px',background:'#fff'}}>
   <div style={{fontSize:'12px',color:'#6b7280',textTransform:'uppercase',letterSpacing:'0.04em'}}>{label}</div>
   <div style={{fontSize:'24px',fontWeight:700,marginTop:'6px'}}>{value}</div>
  </div>
 )
}

export default function Home(){
 const [localStatus,setLocalStatus]=useState('Idle')
 const [jobId,setJobId]=useState('')
 const [report,setReport]=useState<any>(null)
 const [points,setPoints]=useState([])
 const [authToken,setAuthToken]=useState('')
 const [inviteStatus,setInviteStatus]=useState('Ready')
 const polledStatus=useJobPolling(jobId)
 const status=polledStatus || localStatus

 async function submit(e:FormEvent<HTMLFormElement>){
   e.preventDefault()
   setLocalStatus('Uploading...')
   setReport(null)
   setPoints([])

   const formData=new FormData(e.currentTarget)
   const data=await runEvaluation(formData)
   setJobId(data.evaluation_id)
   setLocalStatus(data.status)
 }

 async function submitInvitation(e:FormEvent<HTMLFormElement>){
   e.preventDefault()
   setInviteStatus('Sending...')
   const formData=new FormData(e.currentTarget)
   const email=String(formData.get('email') || '')
   const role=String(formData.get('role') || 'member')
   try{
    await inviteOrganizationUser(email,role,authToken || undefined)
    setInviteStatus('Invitation queued')
    e.currentTarget.reset()
   }catch(error:any){
    setInviteStatus(error?.message || 'Invitation failed')
   }
 }

 useEffect(()=>{
 async function load(){
   if(jobId && status==='COMPLETED'){
      const reportData=await getReport(jobId)
      const pointsData=await getPoints(jobId)
      setReport(reportData)
      setPoints(pointsData.points || [])
   }
 }
 load()
 },[jobId,status])

 return(
 <main style={{maxWidth:'1120px',margin:'40px auto',padding:'24px',fontFamily:'Inter, system-ui, sans-serif'}}>
  <section style={{display:'flex',justifyContent:'space-between',gap:'24px',alignItems:'flex-start',marginBottom:'28px'}}>
   <div>
    <p style={{color:'#4f46e5',fontWeight:700,margin:0}}>PREPARED.ai</p>
    <h1 style={{fontSize:'40px',lineHeight:1.1,margin:'8px 0'}}>BioAI OOD Validation Dashboard</h1>
    <p style={{fontSize:'17px',color:'#4b5563',maxWidth:'700px'}}>
     Turn binding-affinity model claims into reproducible evidence for out-of-distribution generalization.
    </p>
   </div>
   <div style={{border:'1px solid #d1d5db',borderRadius:'999px',padding:'8px 14px',fontSize:'14px',background:'#f9fafb'}}>
    Status: <strong>{status}</strong>
   </div>
  </section>

  <section style={{display:'grid',gridTemplateColumns:'repeat(4,minmax(0,1fr))',gap:'14px',marginBottom:'28px'}}>
   <MetricCard label='Current job' value={jobId ? 'Active' : 'None'} />
   <MetricCard label='Evaluation status' value={status} />
   <MetricCard label='Report' value={report ? 'Ready' : 'Pending'} />
   <MetricCard label='Points loaded' value={String(points.length)} />
  </section>

  <section style={{display:'grid',gridTemplateColumns:'380px 1fr',gap:'24px',alignItems:'start'}}>
   <div style={{display:'grid',gap:'18px'}}>
    <form onSubmit={submit} style={{border:'1px solid #e5e7eb',borderRadius:'16px',padding:'22px',background:'#fff'}}>
     <h2 style={{marginTop:0}}>Run evaluation</h2>
     <label style={{fontWeight:600}}>Model Name</label><br/>
     <input name='model_name' required style={{width:'100%',padding:'10px',margin:'8px 0 16px',border:'1px solid #d1d5db',borderRadius:'8px'}}/><br/>
     <label style={{fontWeight:600}}>Training SHA256</label><br/>
     <input name='training_set_hash' required style={{width:'100%',padding:'10px',margin:'8px 0 16px',border:'1px solid #d1d5db',borderRadius:'8px'}}/><br/>
     <label style={{fontWeight:600}}>Predictions CSV</label><br/>
     <input type='file' name='predictions_file' accept='.csv' required style={{width:'100%',margin:'8px 0 18px'}}/><br/>
     <button type='submit' style={{width:'100%',padding:'12px 16px',borderRadius:'10px',border:0,background:'#4f46e5',color:'#fff',fontWeight:700,cursor:'pointer'}}>Run Evaluation</button>
     {jobId && <p style={{fontSize:'13px',color:'#6b7280',wordBreak:'break-all'}}>Job: {jobId}</p>}
    </form>

    <section style={{border:'1px solid #e5e7eb',borderRadius:'16px',padding:'22px',background:'#fff'}}>
     <h2 style={{marginTop:0}}>Organization access</h2>
     <label style={{fontWeight:600}}>Bearer token</label>
     <textarea value={authToken} onChange={(e)=>setAuthToken(e.target.value)} placeholder='Paste an owner/admin JWT for invitation actions' style={{width:'100%',minHeight:'72px',padding:'10px',margin:'8px 0 16px',border:'1px solid #d1d5db',borderRadius:'8px'}} />
     <form onSubmit={submitInvitation}>
      <label style={{fontWeight:600}}>Invite email</label><br/>
      <input name='email' type='email' required style={{width:'100%',padding:'10px',margin:'8px 0 12px',border:'1px solid #d1d5db',borderRadius:'8px'}} />
      <label style={{fontWeight:600}}>Role</label><br/>
      <select name='role' defaultValue='member' style={{width:'100%',padding:'10px',margin:'8px 0 16px',border:'1px solid #d1d5db',borderRadius:'8px'}}>
       <option value='member'>member</option>
       <option value='admin'>admin</option>
      </select>
      <button type='submit' style={{width:'100%',padding:'12px 16px',borderRadius:'10px',border:'1px solid #4f46e5',background:'#fff',color:'#4f46e5',fontWeight:700,cursor:'pointer'}}>Send Invitation</button>
      <p style={{fontSize:'13px',color:'#6b7280'}}>Invitation status: {inviteStatus}</p>
     </form>
    </section>
   </div>

   <section style={{border:'1px solid #e5e7eb',borderRadius:'16px',padding:'22px',background:'#fff'}}>
    <h2 style={{marginTop:0}}>Evidence package</h2>
    <ReportCard report={report} points={points}/>
   </section>
  </section>
 </main>
 )
}
