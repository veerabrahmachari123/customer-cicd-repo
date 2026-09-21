from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List

# Initialize FastAPI application instance
app = FastAPI(title="Customer Management API")

# --- In-Memory persistence dataset ---
CUSTOMERS_DB: Dict[int, dict] = {
    1: {"id": 1, "name": "John Doe", "email": "john@example.com"},
    2: {"id": 2, "name": "Alice Smith", "email": "alice@example.com"}
}

class Customer(BaseModel):
    id: int
    name: str = Field(..., min_length=2)
    email: str

# --- API Route Endpoints ---

@app.get("/health")
def health_check():
    """
    Mandatory Health Check endpoint matching Jenkins batch curls.
    """
    return {"status": "healthy", "service": "customer-cicd-core"}

@app.get("/environment")
def get_environment():
    return {"environment": "configured"}

@app.get("/version")
def get_version():
    return {"version": "5.0"}

@app.get("/customers", response_model=List[Customer])
def get_all_customers():
    return list(CUSTOMERS_DB.values())

@app.get("/customers/search")
def search_customers(name: str):
    """
    Feature mapping rule matching repository search curls.
    """
    results = [c for c in CUSTOMERS_DB.values() if name.lower() in c["name"].lower()]
    return results
