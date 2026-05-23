from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from .schemas import JobStatus
from .storage import save_upload,write_metadata,read_metadata,delete_job,report_path,points_path
from worker.tasks import evaluate_job
import json

router=APIRouter(prefix='/v1/evaluations',tags=['evaluations'])

@router.post('/run')
async def run(model_name:str=Form(...),training_set_hash:str=Form(...),predictions_file:UploadFile=File(...)):
 job_id=str(uuid4())
 path=await save_upload(job_id,predictions_file)
 write_metadata(job_id,{
 'evaluation_id':job_id,
 'model_name':model_name,
 'training_set_hash':training_set_hash,
 'status':JobStatus.PENDING.value
 })
 evaluate_job.delay(job_id,str(path))
 return {'status':JobStatus.PENDING,'evaluation_id':job_id}

@router.get('/{job_id}')
def status(job_id:str):
 return read_metadata(job_id)

@router.get('/{job_id}/report')
def report(job_id:str):
 p=report_path(job_id)
 if not p.exists():
   raise HTTPException(status_code=404,detail='Report not available')
 return json.loads(p.read_text())

@router.get('/{job_id}/points')
def points(job_id:str):
 p=points_path(job_id)
 if not p.exists():
   raise HTTPException(status_code=404,detail='Points not available')
 return json.loads(p.read_text())

@router.delete('/{job_id}')
def remove(job_id:str):
 delete_job(job_id)
 return {'deleted':True}
