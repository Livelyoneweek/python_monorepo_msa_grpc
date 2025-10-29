import asyncio
import grpc
from math_service.core import add
from shared_protos import math_pb2, math_pb2_grpc


class MathService(math_pb2_grpc.MathServiceServicer):
    async def Add(self, request, context):
        result = add(request.a, request.b)
        return math_pb2.AddReply(result=result)


async def serve(host: str = "0.0.0.0", port: int = 50051):
    server = grpc.aio.server()  # asyncio 서버
    math_pb2_grpc.add_MathServiceServicer_to_server(MathService(), server)
    server.add_insecure_port(f"{host}:{port}")
    print(f"[math_service] gRPC listening on {host}:{port}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
