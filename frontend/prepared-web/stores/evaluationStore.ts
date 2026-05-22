import {create} from 'zustand'

interface EvaluationState{
 jobId:string
 status:string
 setJob:(id:string,status:string)=>void
}

export const useEvaluationStore=create<EvaluationState>((set)=>( {
 jobId:'',
 status:'Idle',
 setJob:(id,status)=>set({jobId:id,status})
}))