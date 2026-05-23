'use client'

import ConfidenceIntervals from './ConfidenceIntervals'
import ParityPlot from './ParityPlot'

type Point={truth:number,prediction:number}

type Report={
 metrics?:Record<string,number>
 cis?:Record<string,[number,number]>
 acceptance?:{
   passed?:boolean
 }
}

export default function ReportCard({report,points=[]}:{report:Report,points?:Point[]}){
if(!report)return null

const metrics=report.metrics || {}
const passed=report.acceptance?.passed

return(
<div style={{marginTop:'30px'}}>
<h2>Evaluation Report</h2>

<div style={{padding:'10px',border:'1px solid gray',marginBottom:'15px'}}>
Status: {passed ? 'PASSED':'FAILED'}
</div>

<div style={{display:'grid',gridTemplateColumns:'repeat(2,1fr)',gap:'10px'}}>
{Object.entries(metrics).map(([k,v])=>(
<div key={k} style={{border:'1px solid #334155',padding:'12px'}}>
<div>{k}</div>
<strong>{Number(v).toFixed(4)}</strong>
</div>
))}
</div>

<ConfidenceIntervals cis={report.cis}/>
<ParityPlot points={points}/>
</div>
)
}
