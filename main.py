import requests
import logging
import urllib3
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Remove os avisos de SSL no terminal para não poluir os logs do Render
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

# SISTEMA DE REDUNDÂNCIA (DESCENTRALIZAÇÃO DE FONTE)
# Agora inclui .io e .com para a BrasilAPI e ignora erro de SSL
PRICE_SOURCES = [
    {"name": "AwesomeAPI", "url": "https://economia.awesomeapi.com.br/last/USD-BRL", "parser": lambda d: float(d['USD']['bid'])},
    {"name": "Binance", "url": "https://api.binance.com/api/v3/ticker/price?symbol=USDTBRL", "parser": lambda d: float(d['price'])},
    {"name": "BrasilAPI_IO", "url": "https://brasilapi.io/api/usd", "parser": lambda d: float(d['usd'])},
    {"name": "BrasilAPI_COM", "url": "https://brasilapi.com/api/usd", "parser": lambda d: float(d['usd'])}
]

class SimulationRequest(BaseModel):
    amount: float

class TransactionRequest(BaseModel):
    amount: float
    pix_key: str

def get_usdt_price():
    """
    Tenta obter a cotação de múltiplas fontes. 
    Usa verify=False para ignorar certificados SSL expirados.
    """
    for source in PRICE_SOURCES:
        try:
            # verify=False ignora o erro de certificado expirado que estava travando seu log
            response = requests.get(source["url"], timeout=3, verify=False) 
            if response.status_code == 200:
                price = source["parser"](response.json())
                logger.info(f"Cotação obtida via {source['name']}: {price}")
                return price
        except Exception as e:
            logger.warning(f"Falha na fonte {source['name']}: {e}")
            continue 
    
    logger.error("TODAS as fontes de cotação falharam. Usando fallback estático.")
    return 5.60 # Valor de segurança caso a internet caia totalmente

@app.get("/check_status")
async def check_status():
    return {"status": "online", "version": "2.6.6-AI-Redundant"}

@app.post("/simulate")
async def simulate(request: SimulationRequest, x_api_key: str = Header(None)):
    if x_api_key != MASTER_API_KEY:
        logger.warning(f"Acesso negado. Chave: {x_api_key}")
        raise HTTPException(status_code=403, detail="API Key Inválida")

    price = get_usdt_price()
    # Spread de lucro (3.5%)
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
