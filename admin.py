import hmac
import hashlib
import os
from fastapi import APIRouter, Depends, HTTPException, Header
from database import get_db

router = APIRouter(prefix='/admin')

def verify_token(x_token: str = Header(None)):
    secret = os.getenv('CRYPTOPIX_SECRET_KEY', 'default_secret')
    password = os.getenv('CRYPTOPIX_ADMIN_PASSWORD', 'admin123')
    if not x_token or not hmac.compare_digest(x_token, secret):
        raise HTTPException(status_code=403, detail='Token Inválido')
    return True

@router.get('/stats', dependencies=[Depends(verify_token)])
async def get_stats():
    with get_db() as conn:
        total = conn.execute('SELECT COUNT(*) as count FROM operations').fetchone()['count']
        pending = conn.execute('SELECT COUNT(*) as count FROM operations WHERE status=\'pending\'').fetchone()['count']
        return {'total_operations': total, 'pending_payments': pending}

@router.post('/confirm/{op_id}', dependencies=[Depends(verify_token)])
async def confirm_op(op_id: str):
    from state_machine import transition_operation
    transition_operation(op_id, 'confirmed')
    return {'status': 'Operation confirmed'}
