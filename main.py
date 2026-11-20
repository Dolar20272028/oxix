from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cryptopix")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ESSA CHAVE DEVE SER IGUAL NO FRONTEND
MASTER_API_KEY = "genesis_ai_secret_2026"

class SimulationRequest(BaseModel):
    amount: float

class TransactionRequest(BaseModel):
    amount: float
    pix_key: str

def get_usdt_price():
    try:
        response = requests.get("https://brasilapi.com/api/usd", timeout=5)
        data = response.json()
        return data['usd']['bid']
    except Exception as e:
        logger.error(f"Erro cotação: {e}")
        return 5.60

@app.get("/check_status")
async def check_status():
    return {"status": "online"}

@app.post("/simulate")
async def simulate(request: SimulationRequest, x_api_key: str = Header(None)):
    if x_api_key != MASTER_API_KEY:
        logger.warning(f"Tentativa de acesso com chave errada: {x_api_key}")
        raise HTTPException(status_code=403, detail="API Key Inválida")

    price = get_usdt_price()
    spread = 1.035 
    final_value = request.amount * price * spread
    
    return {
        "amount": request.amount,
        "price": price,
        "final_value": round(final_value, 2)
    }

@app.post("/create_transaction")
async def create_transaction(request: TransactionRequest, x_api_key: str = Header(None)):
    if x_api_key != MASTER_API_KEY:
        raise HTTPException(status_code=403, detail="API Key Inválida")

    logger.info(f"NOVA TRANSAÇÃO: {request.amount} USDT | PIX: {request.pix_key}")
    
    return {
        "status": "pending",
        "wallet": "TMN2ShY4KSex1gtc68AL9LziXr8i4RdFYM",
        "network": "TRC20"
    }
