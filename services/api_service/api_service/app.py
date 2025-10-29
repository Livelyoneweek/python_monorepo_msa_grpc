from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
import grpc
from shared_protos import math_pb2, math_pb2_grpc


GRPC_TARGET = "localhost:50051"  # math_service gRPC 서버 주소

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 gRPC 채널/스텁 생성
    app.state.grpc_channel = grpc.aio.insecure_channel(GRPC_TARGET)
    app.state.math_stub = math_pb2_grpc.MathServiceStub(app.state.grpc_channel)
    try:
        yield
    finally:
        # 앱 종료 시 정리
        await app.state.grpc_channel.close()

# app = FastAPI(title="API Service")
app = FastAPI(title="API Service (calls gRPC)", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}

# @app.get("/add")
# def add_route(a: int, b: int):
#     return {"result": add(a, b)}

@app.get("/add")
async def add_route(a: int, b: int):
    try:
        req = math_pb2.AddRequest(a=a, b=b)
        resp = await app.state.math_stub.Add(req, timeout=3.0)
        return {"result": resp.result}
    except grpc.aio.AioRpcError as e:
        # gRPC 에러를 HTTP로 매핑
        raise HTTPException(status_code=502, detail=f"gRPC error: {e.code().name}")