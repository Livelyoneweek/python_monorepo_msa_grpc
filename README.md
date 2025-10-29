# 🧩 Monorepo-based gRPC Microservice Architecture  
**(Python + FastAPI + gRPC + uv)**

이 프로젝트는 **하나의 Monorepo** 내에서 **MSA (Microservice Architecture)** 를 구성하는 예제입니다.  
각 서비스는 독립된 Python 패키지로 구성되며, 서비스 간 통신은 **gRPC** 를 통해 이루어집니다.

---

## 📁 프로젝트 구조

```
43_python_mono_grpc/
├── pyproject.toml                  # uv workspace 설정
│   └── [tool.uv.workspace]
│       members = [
│           "services/api_service",
│           "services/math_service",
│           "services/shared_protos"
│       ]
│
└── services/
    ├── api_service/
    │   ├── api_service/app.py      # FastAPI → gRPC Client
    │   └── pyproject.toml
    │
    ├── math_service/
    │   ├── math_service/core.py    # 비즈니스 로직 (add 함수)
    │   ├── math_service/server.py  # gRPC 서버
    │   └── pyproject.toml
    │
    └── shared_protos/
        ├── shared_protos/
        │   ├── __init__.py
        │   ├── math.proto
        │   ├── math_pb2.py
        │   ├── math_pb2_grpc.py
        └── pyproject.toml
```

---

## 🧠 개념 정리

| 개념 | 설명 |
|------|------|
| **Monorepo** | 여러 서비스를 한 Git 리포지토리에서 관리 |
| **MSA** | 각 서비스가 독립적으로 실행되며, 네트워크(gRPC)로 통신 |
| **shared_protos** | 모든 서비스가 공통으로 사용하는 gRPC 계약(proto) 및 stub 코드 보관소 |
| **api_service** | HTTP Gateway (FastAPI) — gRPC 클라이언트 역할 |
| **math_service** | gRPC 서버 — 실제 비즈니스 로직 수행 |

---

## 🧩 서비스 간 관계

```
[ FastAPI (api_service) ]
           │
           │  gRPC 호출
           ▼
[ gRPC Server (math_service) ]
           │
           ▼
  add(a, b) → result 반환
```

---

## ⚙️ 주요 구성 요소

### ✅ shared_protos (공통 proto/stub 패키지)

**파일:**  
`services/shared_protos/shared_protos/math.proto`

```proto
syntax = "proto3";

package math;

service MathService {
  rpc Add (AddRequest) returns (AddReply);
}

message AddRequest {
  int32 a = 1;
  int32 b = 2;
}

message AddReply {
  int32 result = 1;
}
```

**코드 생성 명령어:**

```bash
uv run --directory services/shared_protos python -m grpc_tools.protoc   -I shared_protos   --python_out=shared_protos   --grpc_python_out=shared_protos   shared_protos/math.proto
```

---

### ✅ math_service (gRPC 서버)

**파일:**  
`services/math_service/math_service/server.py`

```python
import grpc
import asyncio
from math_service.core import add
from shared_protos import math_pb2, math_pb2_grpc

class MathService(math_pb2_grpc.MathServiceServicer):
    async def Add(self, request, context):
        result = add(request.a, request.b)
        return math_pb2.AddReply(result=result)

async def serve():
    server = grpc.aio.server()
    math_pb2_grpc.add_MathServiceServicer_to_server(MathService(), server)
    server.add_insecure_port("[::]:50051")
    print("[math_service] gRPC listening on 50051")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
```

---

### ✅ api_service (FastAPI → gRPC Client)

**파일:**  
`services/api_service/api_service/app.py`

```python
from fastapi import FastAPI, HTTPException
import grpc
from shared_protos import math_pb2, math_pb2_grpc

app = FastAPI()

@app.get("/add")
async def add_route(a: int, b: int):
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = math_pb2_grpc.MathServiceStub(channel)
        try:
            resp = await stub.Add(math_pb2.AddRequest(a=a, b=b))
            return {"result": resp.result}
        except grpc.aio.AioRpcError as e:
            raise HTTPException(status_code=502, detail=str(e))
```

---

## 🚀 실행 순서

1️⃣ **shared_protos 빌드**
```bash
uv run --directory services/shared_protos python -m grpc_tools.protoc   -I shared_protos   --python_out=shared_protos   --grpc_python_out=shared_protos   shared_protos/math.proto
```

2️⃣ **math_service (gRPC 서버) 실행**
```bash
uv run --directory services/math_service python -m math_service.server
```

3️⃣ **api_service (FastAPI) 실행**
```bash
uv run --directory services/api_service uvicorn api_service.app:app --reload --port 8000
```

4️⃣ **테스트**
```bash
GET http://127.0.0.1:8000/add?a=3&b=5
```
➡️ 응답:  
```json
{"result": 8}
```

---

## 🧰 핵심 포인트 요약

| 항목 | 설명 |
|------|------|
| **서비스 분리** | `api_service`, `math_service` 각각 독립 실행 |
| **통신 방식** | gRPC (proto 기반 stub 사용) |
| **코드 공유 금지** | 서비스 간 직접 import ❌ → `shared_protos` 로만 연결 |
| **워크스페이스 관리** | 루트 `pyproject.toml` 에서 uv workspace 구성 |
| **빌드 관리** | `grpc_tools.protoc` 로 stub 자동 생성 |

---

## 📦 확장 아이디어

- 새로운 서비스(`string_service`, `stats_service` 등) 추가 시 **proto만 shared_protos에 추가**
- **Docker Compose** 로 여러 서비스 동시 구동
- **CI/CD 파이프라인** 에서 `make proto` 자동화

---

## 🧩 요약 문장

> 이 프로젝트는 **하나의 Monorepo** 안에서  
> **FastAPI + gRPC** 를 이용해 **MSA 구조**를 구현한 예제입니다.  
> 모든 서비스는 **공통 proto 정의(shared_protos)** 를 통해 계약 기반으로 통신하며,  
> 각 서비스는 **완전히 독립적인 Python 패키지**로 구성됩니다.
