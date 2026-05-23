'use client'

type Point={truth:number,prediction:number}

export default function ParityPlot({points=[]}:{points?:Point[]}){
 const width=300
 const height=300
 const max=Math.max(...points.flatMap(p=>[p.truth,p.prediction]),10)

 return(
 <section style={{marginTop:'24px'}}>
 <h3>Parity Plot</h3>
 <svg width={width} height={height} style={{border:'1px solid #334155'}}>
 <line x1='0' y1={height} x2={width} y2='0' stroke='gray'/>
 {points.map((p,i)=>{
 const x=(p.truth/max)*width
 const y=height-(p.prediction/max)*height
 return <circle key={i} cx={x} cy={y} r='4'/>
 })}
 </svg>
 </section>
 )
}
