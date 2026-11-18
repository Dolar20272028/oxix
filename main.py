from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uuid

app = FastAPI()

# Libera o acesso para o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class OperationCreate(BaseModel):
    amount: float = Field(..., gt=0, lt=1000001)
    currency: str

@app.get("/")
async def root():
    return {"status": "CryptoPix API Online"}

@app.post("/simulate")
async def simulate_operation(op: OperationCreate):
    # Simulação de cotação (Ex: 1 USD = 5.50 BRL)
    quote = 5.50 
    result = op.amount / quote
    transaction_id = f"CPX-{uuid.uuid4().hex[:8].upper()}"
    
    return {
        "transaction_id": transaction_id,
        "amount_brl": op.amount,
        "converted_amount": round(result, 8),
        "currency": op.currency,
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
