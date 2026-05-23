'use client'

type Point={truth:number,prediction:number}

export default function ParityPlot({points=[]}:{points?:Point[]}){
 const width=420
 const height=340
 const pad=44
 const plotW=width-pad*2
 const plotH=height-pad*2

 if(points.length===0){
   return <section style={{marginTop:'24px'}}><h3>Parity Plot</h3><p>No parity points available yet.</p></section>
 }

 const values=points.flatMap(p=>[p.truth,p.prediction])
 const min=Math.min(...values)
 const max=Math.max(...values)
 const span=max-min || 1
 const lo=min-span*0.08
 const hi=max+span*0.08
 const scale=(v:number)=>((v-lo)/(hi-lo))

 return(
 <section style={{marginTop:'24px'}}>
 <h3>Parity Plot</h3>
 <svg width={width} height={height} style={{border:'1px solid #334155',background:'#020617'}}>
 <line x1={pad} y1={height-pad} x2={width-pad} y2={height-pad} stroke='#64748b'/>
 <line x1={pad} y1={height-pad} x2={pad} y2={pad} stroke='#64748b'/>
 <line x1={pad} y1={height-pad} x2={width-pad} y2={pad} stroke='#94a3b8' strokeDasharray='4 4'/>
 <text x={width/2-35} y={height-8} fill='#cbd5e1' fontSize='12'>Ground Truth</text>
 <text x='8' y='20' fill='#cbd5e1' fontSize='12'>Prediction</text>
 <text x={pad} y={height-pad+18} fill='#94a3b8' fontSize='10'>{lo.toFixed(2)}</text>
 <text x={width-pad-30} y={height-pad+18} fill='#94a3b8' fontSize='10'>{hi.toFixed(2)}</text>
 {points.map((p,i)=>{
 const x=pad+scale(p.truth)*plotW
 const y=height-pad-scale(p.prediction)*plotH
 return <circle key={i} cx={x} cy={y} r='4' fill='#38bdf8'><title>{`${p.truth} → ${p.prediction}`}</title></circle>
 })}
 </svg>
 </section>
 )
}
