from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form
from .schemas import JobStatus
from .storage import save_upload,write_metadata,read_metadata,delete_job
from worker.tasks import evaluate_job

router=APIRouter(prefix='/v1/evaluations',tags=['evaluations'])

@router.post('/run')
async def run(
 model_name:str=Form(...),
 training_set_hash:str=Form(...),
 predictions_file:UploadFile=File(...)
):
 job_id=str(uuid4())
 path=await save_upload(job_id,predictions_file)

 write_metadata(job_id,{
 'evaluation_id':job_id,
 'model_name':model_name,
 'training_set_hash':training_set_hash,
 'status':JobStatus.PENDING.value
 })

 evaluate_job.delay(job_id,str(path))

 return {
 'status':JobStatus.PENDING,
 'evaluation_id':job_id
 }

@router.get('/{job_id}')
def status(job_id:str):
 return read_metadata(job_id)

@router.delete('/{job_id}')
def remove(job_id:str):
 delete_job(job_id)
 return {'deleted':True}
