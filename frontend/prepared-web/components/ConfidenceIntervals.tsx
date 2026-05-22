'use client'

type Props={
  cis?:Record<string,[number,number]>
}

export default function ConfidenceIntervals({cis}:Props){
 if(!cis)return null

 return(
  <section style={{marginTop:'24px'}}>
   <h3>Bootstrap Confidence Intervals</h3>
   <div style={{display:'grid',gridTemplateColumns:'repeat(2,1fr)',gap:'10px'}}>
    {Object.entries(cis).map(([metric,range])=>(
     <div key={metric} style={{border:'1px solid #334155',padding:'12px'}}>
      <div>{metric}</div>
      <strong>{Number(range[0]).toFixed(4)} – {Number(range[1]).toFixed(4)}</strong>
     </div>
    ))}
   </div>
  </section>
 )
}
