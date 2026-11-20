from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
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
# Agora usamos Spread (Lucro) em vez de taxa fixa descontada
SPREAD_PERCENT = 3.5 
WALLET_ADDRESS = "TMN2ShY4KSex1gtc68AL9LziXr8i4RdFYM"
MASTER_API_KEY = "GENESIS_AI_SECRET_2026"

transaction_ledger = {}

class TransactionRequest(BaseModel):
    amount: float
    pix_key: str
    agent_id: Optional[str] = "human_user"
    webhook_url: Optional[str] = None

async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != MASTER_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

async def get_real_usdt_rate():
    """Busca a cotação real do Dólar via AwesomeAPI"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://economia.awesomeapi.com.br/last/USD-BRL")
            data = response.json()
            return float(data["USDBRL"]["bid"])
    except Exception:
        return 5.70  # Fallback caso a API caia

@app.get("/")
async def root():
    return {"protocol": "CryptoPix Genesis", "status": "Operational"}

@app.get("/simulate")
async def simulate(amount: float, asset: str):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    # 1. Pega a cotação real do mercado
    market_rate = await get_real_usdt_rate()
    
    # 2. Aplica o Spread de 3,5% (O cliente paga um pouco mais caro que o mercado)
    # Formula: Valor = (Quantidade * Cotação) * (1 - 0.035) -> Isso é a liquidação líquida para o cliente
    final_amount = (amount * market_rate) * (1 - (SPREAD_PERCENT / 100))
    
    return {
        "quote": {
            "final_amount": round(final_amount, 2),
            "market_rate": market_rate,
            "spread_percent": SPREAD_PERCENT,
            "currency": "BRL",
            "timestamp": time.time()
        }
    }

@app.post("/create_transaction")
async def create_transaction(req: TransactionRequest):
    try:
        tx_id = f"GEN-AI-{uuid.uuid4().hex[:8].upper()}"
        transaction_ledger[tx_id] = {
            "amount": req.amount,
            "pix_key": req.pix_key,
            "agent": req.agent_id,
            "status": "PENDING_DEPOSIT",
            "timestamp": time.time()
        }
        return {
            "status": "success",
            "transaction_id": tx_id,
            "wallet": WALLET_ADDRESS
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/status/{tx_id}", dependencies=[Depends(verify_api_key)])
async def get_agent_status(tx_id: str):
    if tx_id not in transaction_ledger:
        raise HTTPException(status_code=404, detail="Not found")
    return {"transaction_id": tx_id, "data": transaction_ledger[tx_id]}

@app.post("/agent/update_status/{tx_id}", dependencies=[Depends(verify_api_key)])
async def update_status(tx_id: str, status: str):
    if tx_id not in transaction_ledger:
        raise HTTPException(status_code=404, detail="Not found")
    transaction_ledger[tx_id]["status"] = status
    return {"status": "updated", "new_status": status}
