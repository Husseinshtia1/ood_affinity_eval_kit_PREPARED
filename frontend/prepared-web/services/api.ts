const API_URL=process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function requestJson(url:string,options?:RequestInit){
 const res=await fetch(url,options)
 const data=await res.json().catch(()=>null)
 if(!res.ok){
   throw new Error(data?.detail || `Request failed with status ${res.status}`)
 }
 return data
}

export async function runEvaluation(formData:FormData){
 return requestJson(`${API_URL}/v1/evaluations/run`,{
   method:'POST',
   body:formData
 })
}

export async function getStatus(jobId:string){
 return requestJson(`${API_URL}/v1/evaluations/${jobId}`)
}

export async function getReport(jobId:string){
 return requestJson(`${API_URL}/v1/evaluations/${jobId}/report`)
}

export async function getPoints(jobId:string){
 return requestJson(`${API_URL}/v1/evaluations/${jobId}/points`)
}
