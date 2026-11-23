import os
import requests
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_COINGECKO = os.getenv("COINGECKO_API_KEY", "")

cached_price = None
last_fetch_time = 0
CACHE_DURATION = 600 

class SimulationRequest(BaseModel):
    amount: float

def get_dynamic_rate(amount: float, base_rate: float):
    if amount >= 50000: return base_rate * 1.001 
    elif amount >= 10000: return base_rate * 1.005
    elif amount >= 1000: return base_rate * 1.01
    else: return base_rate * 1.02

def fetch_usdt_price():
    global cached_price, last_fetch_time
    current_time = time.time()
    if cached_price and (current_time - last_fetch_time < CACHE_DURATION):
        return cached_price
    try:
        # USANDO A PORTA DEMO (x_cg_demo_api_key) PORQUE SUA CHAVE É DEMO
        url = f"https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=brl&x_cg_demo_api_key={API_KEY_COINGECKO}"
        response = requests.get(url, timeout=10)
        if response.status_code == 429:
            return cached_price if cached_price else 5.60
        response.raise_for_status()
        data = response.json()
        cached_price = float(data['tether']['brl'])
        last_fetch_time = current_time
        return cached_price
    except Exception as e:
        logger.error(f"Erro API: {e}")
        return cached_price if cached_price else 5.60

@app.get("/check_status")
async def check_status():
    return {"status": "online", "source": "CoinGecko Demo API"}

@app.post("/simulate")
async def simulate(request: SimulationRequest):
    if request.amount <= 0 or request.amount > 100000000:
        raise HTTPException(status_code=400, detail="Valor inválido.")

    base_rate = fetch_usdt_price()
    final_rate = get_dynamic_rate(request.amount, base_rate)
    total_brl = request.amount * final_rate
    
    return {
        "amount": request.amount,
        "base_rate": round(base_rate, 2),
        "final_rate": round(final_rate, 4),
        "total_brl": round(total_brl, 2),
        "message": "Cotação calculada com sucesso via Demo API."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
