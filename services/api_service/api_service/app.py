from fastapi import FastAPI
from math_service.core import add

app = FastAPI(title="API Service")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/add")
def add_route(a: int, b: int):
    return {"result": add(a, b)}
