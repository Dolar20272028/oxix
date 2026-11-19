from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from state_machine import initialize_state_schema
from admin import router as admin_router

app = FastAPI()

# Permite que o seu frontend no GitHub Pages acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota de teste para saber se está Live
@app.get("/check_status")
async def check_status():
    return {"status": "online", "message": "API CryptoPix Genesis está operacional"}

# Inclui as rotas do admin
app.include_router(admin_router)

@app.on_event("startup")
async def startup_event():
    initialize_state_schema()

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API CryptoPix. Use /check_status para testar."}
