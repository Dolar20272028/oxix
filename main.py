from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações de Taxa Embutida (Aumentada para cobrir o custo do Gateway)
USDT_RATE = 5.70 
FEE_PERCENT = 5.0 # Taxa de 5% para cobrir Gateway + Lucro Líquido
WALLET_ADDRESS = "TMN2ShY4KSex1gtc68AL9LziXr8i4RdFYM"

class TransactionRequest(BaseModel):
    amount: float
    pix_key: str # Agora exigimos a chave PIX

@app.get("/")
async def root():
    return {"message": "API CryptoPix Genesis - Modo Autônomo Ativo", "status": "Live"}

@app.get("/simulate")
async def simulate(amount: float, asset: str):
    try:
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Valor inválido")
        
        fee_amount = amount * (FEE_PERCENT / 100)
        final_amount = (amount - fee_amount) * USDT_RATE
        
        return {
            "final_amount": final_amount,
            "fee_percent": FEE_PERCENT,
            "fee_amount": fee_amount
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_transaction")
async def create_transaction(req: TransactionRequest):
    try:
        # Aqui o sistema registra a chave PIX para a liquidação posterior
        transaction_id = f"GEN-{random.randint(100000, 999999)}"
        
        # LOG de Orquestração: Aqui entraria a chamada para a API do Gateway Offshore
        print(f"Nova transação: {transaction_id} | Valor: {req.amount} | Destino PIX: {req.pix_key}")
        
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "wallet": WALLET_ADDRESS,
            "pix_key_registered": req.pix_key,
            "message": "Aguardando confirmação na rede TRC20 para liberação do PIX"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
