from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from .schemas import JobStatus
from .storage import save_upload,write_metadata,read_metadata,delete_job,report_path,points_path
from .auth_dependencies import get_current_user
from .database import get_db
from .models import User, Evaluation
from worker.tasks import evaluate_job
import json

router=APIRouter(prefix='/v1/evaluations',tags=['evaluations'])


def assert_job_owner(job_id:str,current_user:User,db:Session):
 evaluation=db.query(Evaluation).filter(Evaluation.job_id==job_id).first()
 if not evaluation:
   raise HTTPException(status_code=404,detail='Evaluation not found')
 if evaluation.owner_id != current_user.id:
   raise HTTPException(status_code=403,detail='Not authorized for this evaluation')
 return evaluation

@router.post('/run')
async def run(
 model_name:str=Form(...),
 training_set_hash:str=Form(...),
 predictions_file:UploadFile=File(...),
 current_user:User=Depends(get_current_user),
 db:Session=Depends(get_db)
):
 job_id=str(uuid4())
 path=await save_upload(job_id,predictions_file)

 evaluation=Evaluation(job_id=job_id,owner_id=current_user.id,status=JobStatus.PENDING.value)
 db.add(evaluation)
 db.commit()

 write_metadata(job_id,{
 'evaluation_id':job_id,
 'model_name':model_name,
 'training_set_hash':training_set_hash,
 'status':JobStatus.PENDING.value,
 'owner_id':current_user.id,
 'organization_id':current_user.organization_id
 })
 evaluate_job.delay(job_id,str(path))
 return {'status':JobStatus.PENDING,'evaluation_id':job_id}

@router.get('/{job_id}')
def status(job_id:str,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 evaluation=assert_job_owner(job_id,current_user,db)
 metadata=read_metadata(job_id)
 metadata['db_status']=evaluation.status
 return metadata

@router.get('/{job_id}/report')
def report(job_id:str,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 assert_job_owner(job_id,current_user,db)
 p=report_path(job_id)
 if not p.exists():
   raise HTTPException(status_code=404,detail='Report not available')
 return json.loads(p.read_text())

@router.get('/{job_id}/points')
def points(job_id:str,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 assert_job_owner(job_id,current_user,db)
 p=points_path(job_id)
 if not p.exists():
   raise HTTPException(status_code=404,detail='Points not available')
 return json.loads(p.read_text())

@router.delete('/{job_id}')
def remove(job_id:str,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 assert_job_owner(job_id,current_user,db)
 delete_job(job_id)
 db.query(Evaluation).filter(Evaluation.job_id==job_id).delete()
 db.commit()
 return {'deleted':True}
