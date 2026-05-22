'use client'

export default function ReportCard({report}:{report:any}){
if(!report)return null

return(
<div>
<h2>Evaluation Report</h2>
<pre>{JSON.stringify(report,null,2)}</pre>
</div>
)
}
