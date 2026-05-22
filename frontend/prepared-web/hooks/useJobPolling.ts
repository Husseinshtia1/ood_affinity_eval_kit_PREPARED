import {useEffect,useState} from 'react'
import {getStatus} from '../services/api'

const TERMINAL=['COMPLETED','FAILED']

export function useJobPolling(jobId:string){
 const [status,setStatus]=useState('')

 useEffect(()=>{
 if(!jobId)return

 const timer=setInterval(async()=>{
 const result=await getStatus(jobId)
 setStatus(result.status)

 if(TERMINAL.includes(result.status)){
   clearInterval(timer)
 }
 },3000)

 return ()=>clearInterval(timer)
 },[jobId])

 return status
}
