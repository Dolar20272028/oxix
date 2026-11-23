import requests
import logging
import urllib3
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Remove os avisos de SSL no terminal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cryptopix")

app = FastAPI()

# CORS configurado para aceitar requisições do seu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CHAVE DE SEGURANÇA SINCRONIZADA COM O FRONTEND
MASTER_API_KEY = "genesis_ai_secret_2026"

# NOVA LISTA DE FONTES - PRIORIZANDO COINGECKO (MAIS ESTÁVEL NO RENDER)
PRICE_SOURCES = [
    {
        "name": "CoinGecko", 
        "url": "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=brl", 
        "parser": lambda d: float(d['tether']['brl'])
    },
    {
        "name": "AwesomeAPI", 
        "url": "https://economia.awesomeapi.com.br/last/USD-BRL", 
        "parser": lambda d: float(d['USD']['bid'])
    },
    {
        "name": "Binance", 
        "url": "https://api.binance.com/api/v3/ticker/price?symbol=USDTBRL", 
        "parser": lambda d: float(d['price'])
    }
]

class SimulationRequest(BaseModel):
    amount: float

class TransactionRequest(BaseModel):
    amount: float
    pix_key: str

def get_usdt_price():
    """
    Tenta obter a cotação priorizando CoinGecko para evitar bloqueios de IP do Render.
    """
    for source in PRICE_SOURCES:
        try:
            logger.info(f"Tentando conectar na fonte {source['name']}...")
            response = requests.get(source["url"], timeout=10, verify=False) 
            
            if response.status_code == 200:
                price = source["parser"](response.json())
                logger.info(f"SUCESSO! Cotação obtida via {source['name']}: {price}")
                return price
            else:
                logger.warning(f"Fonte {source['name']} respondeu com status {response.status_code}")
        
        except Exception as e:
            logger.error(f"ERRO na fonte {source['name']}: {type(e).__name__} - {str(e)}")
            continue 
    
    logger.error("CRÍTICO: Todas as fontes falharam. Usando fallback 5.60.")
    return 5.60

@app.get("/check_status")
async def check_status():
    return {"status": "online", "version": "2.6.9-AI-CoinGecko"}

@app.post("/simulate")
async def simulate(request: SimulationRequest, x_api_key: str = Header(None)):
    if x_api_key != MASTER_API_KEY:
        logger.warning(f"Acesso negado. Chave: {x_api_key}")
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

@app.get("/")
async def root():
    return {"status": "Online", "message": "CryptoPix API is running"}
