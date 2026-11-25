import os
import time
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
from collections import defaultdict

# --- CONFIGURAÇÃO DE LOGS ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CryptoPix_Bunker")

attack_logger = logging.getLogger("AttackLogger")
handler = logging.FileHandler("attackers.log")
handler.setFormatter(logging.Formatter('%(asctime)s - IP: %(client_ip)s - Agent: %(user_agent)s - Path: %(path)s'))
attack_logger.addHandler(handler)
attack_logger.setLevel(logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

request_history = defaultdict(list)
RATE_LIMIT = 20  
TIME_WINDOW = 60 

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    request_history[client_ip] = [t for t in request_history[client_ip] if now - t < TIME_WINDOW]
    if len(request_history[client_ip]) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Too many requests. Slow down."})
    request_history[client_ip].append(now)
    return await call_next(request)

# Modelos para as rotas de execução
class TransactionRequest(BaseModel):
    amount: float
    pix_key: str

# --- CONFIGURAÇÕES DE NEGÓCIO ---
FALLBACK_PRICE = 5.60
PROFIT_MARGIN = 0.065  # 6.5% de lucro real
MAX_LIMIT = 10000.0    # Trava de 10k USDT

def get_usdt_price():
    try:
        # CoinGecko é estável, mas pode dar rate limit no Render. 
        # Se falhar, cai no fallback.
        url = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=brl"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['tether']['brl'])
    except Exception as e:
        logger.error(f"Erro na cotação: {e}. Usando fallback.")
        return FALLBACK_PRICE

# Alterado para GET para bater com o seu Frontend
@app.get("/api/v1/calc_7x")
async def simulate(amount: float = 0):
    if amount <= 0:
        return JSONResponse(status_code=400, content={"error": "Valor inválido"})
    
    if amount > MAX_LIMIT:
        return JSONResponse(status_code=400, content={"error": f"Limite máximo de {MAX_LIMIT} USDT por operação."})

    market_price = get_usdt_price()
    
    # LÓGICA DE LUCRO: 
    # Preço de Mercado - 6.5% = Preço que o cliente recebe
    # Ex: 5.60 - (5.60 * 0.065) = 5.236
    client_price = market_price * (1 - PROFIT_MARGIN)
    total_brl = amount * client_price

    return {
        "status": "success",
        "market_price": round(market_price, 2),
        "client_price": round(client_price, 2),
        "result": round(total_brl, 2),
        "margin": "6.5%"
    }

@app.post("/api/v1/exec_9z")
async def create_transaction(data: TransactionRequest):
    if data.amount > MAX_LIMIT:
        raise HTTPException(status_code=400, detail="Valor excede o limite permitido.")
        
    logger.info(f"NOVO PEDIDO: {data.amount} USDT | PIX: {data.pix_key}")
    return {
        "status": "pending",
        "message": "Pedido registrado. Aguardando depósito de USDT.",
        "wallet": "T3kS...XyZ123" 
    }

@app.get("/admin")
async def admin_honeypot(request: Request):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    path = request.url.path
    attack_logger.info("", extra={"client_ip": client_ip, "user_agent": user_agent, "path": path})
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/health")
async def health():
    return {"status": "online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
