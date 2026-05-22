'use client'

import {FormEvent,useEffect,useState} from 'react'
import {runEvaluation,getReport} from '../services/api'
import {useJobPolling} from '../hooks/useJobPolling'
import ReportCard from '../components/ReportCard'

export default function Home(){
 const [localStatus,setLocalStatus]=useState('Idle')
 const [jobId,setJobId]=useState('')
 const [report,setReport]=useState<any>(null)
 const polledStatus=useJobPolling(jobId)
 const status=polledStatus || localStatus

 async function submit(e:FormEvent<HTMLFormElement>){
   e.preventDefault()
   setLocalStatus('Uploading...')
   setReport(null)
   const formData=new FormData(e.currentTarget)
   const data=await runEvaluation(formData)
   setJobId(data.evaluation_id)
   setLocalStatus(data.status)
 }

 useEffect(()=>{
   async function loadReport(){
     if(jobId && status==='COMPLETED'){
       const data=await getReport(jobId)
       setReport(data)
     }
   }
   loadReport()
 },[jobId,status])

 return(
   <main style={{maxWidth:'760px',margin:'50px auto',padding:'24px'}}>
     <h1>PREPARED.ai</h1>
     <p>OOD binding-affinity evaluation workflow.</p>

     <form onSubmit={submit}>
       <label>Model Name</label><br/>
       <input name='model_name' placeholder='BioChem-Dock-v1' required/><br/><br/>

       <label>Training Set SHA256</label><br/>
       <input name='training_set_hash' placeholder='64-character SHA256 hash' required/><br/><br/>

       <label>Predictions CSV</label><br/>
       <input type='file' name='predictions_file' accept='.csv' required/><br/><br/>

       <button type='submit'>Run Evaluation</button>
     </form>

     <section>
       <p>Status: {status}</p>
       {jobId && <p>Job: {jobId}</p>}
     </section>

     <ReportCard report={report}/>
   </main>
 )
}
