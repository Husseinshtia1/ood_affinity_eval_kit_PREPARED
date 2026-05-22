const API_URL=process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function runEvaluation(formData:FormData){
 const res=await fetch(`${API_URL}/v1/evaluations/run`,{
 method:'POST',
 body:formData
 })
 return await res.json()
}

export async function getStatus(jobId:string){
 const res=await fetch(`${API_URL}/v1/evaluations/${jobId}`)
 return await res.json()
}

export async function getReport(jobId:string){
 const res=await fetch(`${API_URL}/v1/evaluations/${jobId}/report`)
 return await res.json()
}
