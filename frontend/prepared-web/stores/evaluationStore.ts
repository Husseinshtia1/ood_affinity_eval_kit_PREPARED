import {create} from 'zustand'

export const useEvaluationStore=create((set)=>( {
 jobId:'',
 status:'Idle',
 setJob:(id:string,status:string)=>set({jobId:id,status})
}))