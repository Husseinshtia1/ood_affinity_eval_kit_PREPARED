from __future__ import annotations

from fastapi import APIRouter

from .hosting_adaptation import hosting_capabilities_dict
from .runtime_mutation import runtime_mutation_plan_dict

router = APIRouter(prefix='/hal', tags=['hosting-adaptation'])


@router.get('/status')
def hal_status():
    return hosting_capabilities_dict()


@router.get('/mutation-plan')
def hal_mutation_plan():
    return runtime_mutation_plan_dict()
