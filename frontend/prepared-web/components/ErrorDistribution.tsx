'use client'

type Point={error?:number,abs_error?:number,within_0_30?:boolean}

export default function ErrorDistribution({points=[]}:{points?:Point[]}){
 if(points.length===0){
   return null
 }

 const bins=[0,0,0,0]
 for(const p of points){
   const e=p.abs_error ?? Math.abs(p.error ?? 0)
   if(e<=0.10) bins[0]++
   else if(e<=0.20) bins[1]++
   else if(e<=0.30) bins[2]++
   else bins[3]++
 }

 const labels=['≤0.10','≤0.20','≤0.30','>0.30']
 const max=Math.max(...bins,1)
 const within=points.filter(p=>p.within_0_30!==false).length
 const outside=points.length-within

 return(
 <section style={{marginTop:'24px'}}>
 <h3>Error Distribution</h3>
 <p style={{fontSize:'12px'}}>Within threshold: {within} / Outside threshold: {outside}</p>
 <div style={{display:'grid',gap:'8px'}}>
 {bins.map((count,i)=>(
 <div key={labels[i]}>
 <div style={{fontSize:'12px'}}>{labels[i]}: {count}</div>
 <div style={{height:'12px',background:'#1e293b'}}>
 <div style={{height:'12px',width:`${(count/max)*100}%`,background:i<3?'#22c55e':'#ef4444'}} />
 </div>
 </div>
 ))}
 </div>
 </section>
 )
}
