'use client'

type Report={
 metrics?:Record<string,number>
 acceptance?:{
   passed?:boolean
 }
}

export default function ReportCard({report}:{report:Report}){
if(!report)return null

const metrics=report.metrics || {}
const passed=report.acceptance?.passed

return(
<div style={{marginTop:'30px'}}>
<h2>Evaluation Report</h2>

<div style={{padding:'10px',border:'1px solid gray',marginBottom:'15px'}}>
Status: {passed ? 'PASSED' : 'FAILED'}
</div>

<div style={{display:'grid',gridTemplateColumns:'repeat(2,1fr)',gap:'10px'}}>
{Object.entries(metrics).map(([k,v])=>(
<div key={k} style={{border:'1px solid #334155',padding:'12px'}}>
<div>{k}</div>
<strong>{Number(v).toFixed(4)}</strong>
</div>
))}
</div>
</div>
)
}
