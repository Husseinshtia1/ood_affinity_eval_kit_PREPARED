from __future__ import annotations

from fastapi import APIRouter

from .hosting_adaptation import hosting_capabilities_dict

router = APIRouter(prefix='/hal', tags=['hosting-adaptation'])


@router.get('/status')
def hal_status():
    return hosting_capabilities_dict()
