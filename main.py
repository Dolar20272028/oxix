from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import time
import uuid
from typing import Optional

app = FastAPI(title="CryptoPix Genesis Protocol", version="2.0.0-AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURAÇÕES DO PROTOCOLO ---
USDT_RATE = 5.70 
FEE_PERCENT = 5.0 
WALLET_ADDRESS = "TMN2ShY4KSex1gtc68AL9LziXr8i4RdFYM"
# Chave mestre para agentes autorizados (Em produção, isso ficaria num banco de dados)
MASTER_API_KEY = "GENESIS_AI_SECRET_2026"

# Banco de dados em memória para rastrear transações de agentes
transaction_ledger = {}

class TransactionRequest(BaseModel):
    amount: float
    pix_key: str
    agent_id: Optional[str] = "human_user"
    webhook_url: Optional[str] = None

# --- MIDDLEWARE DE AUTENTICAÇÃO PARA IAs ---
async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != MASTER_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key: Access Denied to Protocol")
    return x_api_key

@app.get("/")
async def root():
    return {
        "protocol": "CryptoPix Genesis",
        "version": "2.0.0-AI",
        "status": "Operational",
        "endpoints": ["/simulate", "/create_transaction", "/agent/status"]
    }

# --- ENDPOINT DE SIMULAÇÃO (Aberto para Humanos e IAs) ---
@app.get("/simulate")
async def simulate(amount: float, asset: str):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    fee_amount = amount * (FEE_PERCENT / 100)
    final_amount = (amount - fee_amount) * USDT_RATE
    
    return {
        "quote": {
            "final_amount": final_amount,
            "fee_percent": FEE_PERCENT,
            "fee_amount": fee_amount,
            "currency": "BRL",
            "timestamp": time.time()
        }
    }

# --- ENDPOINT DE CRIAÇÃO (O Motor de Liquidação) ---
@app.post("/create_transaction")
async def create_transaction(req: TransactionRequest):
    try:
        tx_id = f"GEN-AI-{uuid.uuid4().hex[:8].upper()}"
        
        # Registro no Ledger (Livro Razão)
        transaction_ledger[tx_id] = {
            "amount": req.amount,
            "pix_key": req.pix_key,
            "agent": req.agent_id,
            "status": "PENDING_DEPOSIT",
            "webhook": req.webhook_url,
            "timestamp": time.time()
        }
        
        # Log de Auditoria para o Dono do Motor
        print(f" [PROTOCOL LOG] TX: {tx_id} | Agent: {req.agent_id} | Amount: {req.amount} USDT | Target: {req.pix_key}")
        
        return {
            "status": "success",
            "transaction_id": tx_id,
            "wallet": WALLET_ADDRESS,
            "instructions": "Awaiting TRC20 confirmation",
            "webhook_status": "Active" if req.webhook_url else "Disabled"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ENDPOINTS EXCLUSIVOS PARA AGENTES AUTÔNOMOS (Protegidos por API Key) ---
@app.get("/agent/status/{tx_id}", dependencies=[Depends(verify_api_key)])
async def get_agent_status(tx_id: str):
    if tx_id not in transaction_ledger:
        raise HTTPException(status_code=404, detail="Transaction not found in ledger")
    
    return {
        "transaction_id": tx_id,
        "data": transaction_ledger[tx_id]
    }

@app.post("/agent/update_status/{tx_id}", dependencies=[Depends(verify_api_key)])
async def update_status(tx_id: str, status: str):
    if tx_id not in transaction_ledger:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction_ledger[tx_id]["status"] = status
    return {"status": "updated", "new_status": status}
