from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API CryptoPix. Use /check_status para testar."}

@app.get("/check_status")
async def check_status():
    return {"status": "online", "message": "Servidor operando normalmente"}
