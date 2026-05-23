'use client'

import {FormEvent,useEffect,useState} from 'react'
import {runEvaluation,getReport,getPoints} from '../services/api'
import {useJobPolling} from '../hooks/useJobPolling'
import ReportCard from '../components/ReportCard'

export default function Home(){
 const [localStatus,setLocalStatus]=useState('Idle')
 const [jobId,setJobId]=useState('')
 const [report,setReport]=useState<any>(null)
 const [points,setPoints]=useState([])
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
 <main style={{maxWidth:'760px',margin:'50px auto',padding:'24px'}}>
 <h1>PREPARED.ai</h1>
 <p>OOD binding-affinity evaluation workflow.</p>

 <form onSubmit={submit}>
 <label>Model Name</label><br/>
 <input name='model_name' required/><br/><br/>
 <label>Training SHA256</label><br/>
 <input name='training_set_hash' required/><br/><br/>
 <label>Predictions CSV</label><br/>
 <input type='file' name='predictions_file' accept='.csv' required/><br/><br/>
 <button type='submit'>Run Evaluation</button>
 </form>

 <p>Status: {status}</p>
 {jobId && <p>Job: {jobId}</p>}

 <ReportCard report={report} points={points}/>
 </main>
 )
}
