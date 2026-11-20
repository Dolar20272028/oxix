from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import logging

# Configuração de Logs para ver a chave PIX no Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cryptopix")

app = FastAPI()

# CORS configurado para aceitar requisições do seu frontend no GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chave de segurança para evitar que qualquer um use sua API
MASTER_API_KEY = "genesis_ai_secret_2026"

class SimulationRequest(BaseModel):
    amount: float

class TransactionRequest(BaseModel):
    amount: float
    pix_key: str

def get_usdt_price():
    try:
        # Busca cotação do Dólar/USDT via AwesomeAPI
        response = requests.get("https://brasilapi.com/api/usd")
        data = response.json()
        return data['usd']['bid']
    except Exception as e:
        logger.error(f"Erro ao buscar cotação: {e}")
        return 5.60  # Valor de fallback caso a API caia

@app.get("/check_status")
async def check_status():
    return {"status": "online", "message": "Servidor CryptoPix Operacional"}

@app.post("/simulate")
async def simulate(request: SimulationRequest, x_api_key: str = Header(None)):
    if x_api_key != MASTER_API_KEY:
        raise HTTPException(status_code=403, detail="API Key Inválida")

    price = get_usdt_price()
    # Spread de 3.5% para lucro e taxas da MEXC
    spread = 1.035 
    
    # Cálculo: Valor USDT * Preço Dólar * Spread
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

    # LOG CRUCIAL: Aqui você verá a chave PIX do cliente nos logs do Render
    logger.info(f"NOVA TRANSAÇÃO: Valor {request.amount} USDT | Chave PIX: {request.pix_key}")
    
    # Aqui entraria a lógica de monitoramento da carteira MEXC
    return {
        "status": "pending",
        "message": "Aguardando depósito de USDT",
        "wallet": "TMN2ShY4KSex1gtc68AL9LziXr8i4RdFYM",
        "network": "TRC20"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
