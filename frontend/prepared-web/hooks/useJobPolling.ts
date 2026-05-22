import {useEffect,useState} from 'react'
import {getStatus} from '../services/api'

export function useJobPolling(jobId:string){
 const [status,setStatus]=useState('')

 useEffect(()=>{
 if(!jobId)return

 const timer=setInterval(async()=>{
 const result=await getStatus(jobId)
 setStatus(result.status)
 },3000)

 return ()=>clearInterval(timer)

 },[jobId])

 return status
}
