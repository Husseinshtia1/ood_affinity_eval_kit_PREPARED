from __future__ import annotations

from fastapi import APIRouter

from .hal_learning import build_hal_learning_summary
from .hal_memory import append_hal_memory_record, read_hal_memory
from .hal_metrics import hal_autonomy_metrics_dict
from .hal_optimizer import runtime_optimization_dict
from .hosting_adaptation import hosting_capabilities_dict
from .runtime_mutation import runtime_mutation_plan_dict

router = APIRouter(prefix='/hal', tags=['hosting-adaptation'])


@router.get('/status')
def hal_status():
    return hosting_capabilities_dict()


@router.get('/mutation-plan')
def hal_mutation_plan():
    return runtime_mutation_plan_dict()


@router.post('/memory/capture')
def hal_memory_capture():
    return append_hal_memory_record()


@router.get('/memory')
def hal_memory(limit: int = 20):
    return {'items': read_hal_memory(limit=limit)}


@router.get('/learning')
def hal_learning(limit: int = 100):
    return build_hal_learning_summary(limit=limit)


@router.get('/optimization')
def hal_optimization():
    return runtime_optimization_dict()


@router.get('/metrics')
def hal_metrics():
    return hal_autonomy_metrics_dict()
