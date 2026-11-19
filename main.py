from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI()

# Liberação total de CORS para o GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações da Exchange
USDT_RATE = 5.70  # Cotação base
FEE_PERCENT = 1.5 # Taxa de serviço 1.5%
WALLET_ADDRESS = "TMN2ShY4KSex1gtc68AL9LziXr8i4RdFYM" # COLOQUE SUA CARTEIRA USDT TRC20 AQUI

class TransactionRequest(BaseModel):
    amount: float

@app.get("/")
async def root():
    return {"message": "API CryptoPix Operacional", "status": "Live"}

@app.get("/check_status")
async def check_status():
    return {"status": "online", "message": "Servidor operando normalmente"}

@app.get("/simulate")
async def simulate(amount: float, asset: str):
    try:
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Valor deve ser maior que zero")
        
        # Cálculo de cotação
        fee_amount = amount * (FEE_PERCENT / 100)
        final_amount = (amount - fee_amount) * USDT_RATE
        
        return {
            "final_amount": final_amount,
            "fee_percent": FEE_PERCENT,
            "fee_amount": fee_amount,
            "asset": asset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_transaction")
async def create_transaction(req: TransactionRequest):
    try:
        # Aqui simulamos a criação de um ID de transação no banco de dados
        transaction_id = f"TX-{random.randint(100000, 999999)}"
        
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "wallet": WALLET_ADDRESS,
            "amount": req.amount,
            "message": "Aguardando depósito na rede TRC20"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
