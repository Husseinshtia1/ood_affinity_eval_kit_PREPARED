const API_URL=process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function authHeaders(token?:string):HeadersInit{
 return token ? {Authorization:`Bearer ${token}`} : {}
}

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

export async function listEvaluations(token?:string){
 return requestJson(`${API_URL}/v1/evaluations`,{
   headers:authHeaders(token)
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

export async function inviteOrganizationUser(email:string,role:string,token?:string){
 return requestJson(`${API_URL}/v1/organizations/invitations`,{
   method:'POST',
   headers:{
    'Content-Type':'application/json',
    ...authHeaders(token)
   },
   body:JSON.stringify({email,role})
 })
}

export async function listOrganizationInvitations(token?:string){
 return requestJson(`${API_URL}/v1/organizations/invitations`,{
   headers:authHeaders(token)
 })
}
