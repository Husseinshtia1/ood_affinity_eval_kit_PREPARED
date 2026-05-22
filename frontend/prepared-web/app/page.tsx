'use client'

import {useState} from 'react'

export default function Home(){
const [status,setStatus]=useState('Idle')
const [jobId,setJobId]=useState('')

async function submit(e:any){
 e.preventDefault()
 setStatus('Uploading...')

 const formData=new FormData(e.target)

 const response=await fetch('http://localhost:8000/v1/evaluations/run',{
 method:'POST',
 body:formData
 })

 const data=await response.json()
 setJobId(data.evaluation_id)
 setStatus(data.status)
}

return(
<div style={{maxWidth:'700px',margin:'50px auto'}}>
<h1>PREPARED.ai</h1>
<form onSubmit={submit}>
<input name='model_name' placeholder='Model Name'/><br/><br/>
<input name='training_set_hash' placeholder='Training Hash'/><br/><br/>
<input type='file' name='predictions_file'/><br/><br/>
<button type='submit'>Run Evaluation</button>
</form>
<p>Status:{status}</p>
<p>Job:{jobId}</p>
</div>
)
}
