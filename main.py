import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configurado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SEGURANÇA: CARREGAMENTO DE CHAVES ---
# Em vez de escrever a chave aqui, o código busca no sistema do Render
# Se não encontrar, ele usa um valor padrão ou retorna erro
API_KEY_COINGECKO = os.getenv("COINGECKO_API_KEY", "chave_padrao_se_nao_houver")
SECRET_TOKEN_ADMIN = os.getenv("ADMIN_SECRET_TOKEN", "token_seguro_padrao")

class SimulationRequest(BaseModel):
    amount: float

def get_dynamic_rate(amount: float, base_rate: float):
    if amount >= 50000:
        return base_rate * 1.001 
    elif amount >= 10000:
        return base_rate * 1.005
    elif amount >= 1000:
        return base_rate * 1.01
    else:
        return base_rate * 1.02

def fetch_usdt_price():
    try:
        # Exemplo de como usar a chave criptografada/ambiente na URL
        url = f"https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=brl&x_cg_pro_api_key={API_KEY_COINGECKO}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data['tether']['brl'])
    except Exception as e:
        logger.error(f"Erro ao buscar cotação: {e}")
        return 5.60

@app.get("/check_status")
async def check_status():
    return {"status": "online", "source": "CoinGecko"}

@app.post("/simulate")
async def simulate(request: SimulationRequest):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="O valor deve ser maior que zero.")
    
    if request.amount > 100000000:
        raise HTTPException(status_code=400, detail="Valor excede o limite operacional.")

    base_rate = fetch_usdt_price()
    final_rate = get_dynamic_rate(request.amount, base_rate)
    total_brl = request.amount * final_rate
    
    return {
        "amount": request.amount,
        "base_rate": round(base_rate, 2),
        "final_rate": round(final_rate, 4),
        "total_brl": round(total_brl, 2),
        "message": "Cotação calculada com taxa de volume aplicada."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
