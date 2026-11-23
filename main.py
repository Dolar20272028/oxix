import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import time

app = FastAPI()

# Blindagem de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "SUA_CHAVE_AQUI")
CACHE_PRICE = {"price": 5.60, "timestamp": 0}
CACHE_DURATION = 600 

class SimulationRequest(BaseModel):
    amount: float

class TransactionRequest(BaseModel):
    amount: float
    pix_key: str

def get_usdt_price():
    global CACHE_PRICE
    current_time = time.time()
    if current_time - CACHE_PRICE["timestamp"] < CACHE_DURATION:
        return CACHE_PRICE["price"]
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "tether", "vs_currencies": "brl", "x_cg_demo_api_key": COINGECKO_API_KEY}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        price = data["tether"]["brl"]
        CACHE_PRICE = {"price": price, "timestamp": current_time}
        return price
    except Exception as e:
        return CACHE_PRICE["price"]

@app.get("/check_status")
async def check_status():
    return {"status": "online", "message": "CryptoPix Backend Operacional"}

@app.post("/simulate")
async def simulate(req: SimulationRequest):
    base_rate = get_usdt_price()
    amount = req.amount
    if amount >= 50000: multiplier = 1.001
    elif amount >= 10000: multiplier = 1.005
    elif amount >= 1000: multiplier = 1.01
    else: multiplier = 1.02
    total_brl = amount * base_rate * multiplier
    return {"base_rate": base_rate, "total_brl": round(total_brl, 2), "multiplier": multiplier}

@app.post("/create_transaction")
async def create_transaction(req: TransactionRequest):
    # --- AQUI ESTÁ O SEGREDO: O PRINT PARA O SEU LOG ---
    print("\n" + "="*50)
    print(f"🚨 NOVO PEDIDO DE TROCA! 🚨")
    print(f"CHAVE PIX DO CLIENTE: {req.pix_key}")
    print(f"VALOR EM USDT: {req.amount}")
    print("="*50 + "\n")
    # -------------------------------------------------

    wallet_address = "TXs1aB2c3D4e5F6g7H8i9J0kLmMnNoOpQrS" # Sua carteira USDT
    return {
        "status": "success",
        "wallet": wallet_address,
        "amount_usdt": req.amount,
        "pix_key": req.pix_key
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
