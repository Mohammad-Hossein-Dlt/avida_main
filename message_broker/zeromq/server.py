import asyncio
import json
import zmq.asyncio
from typing import Tuple


async def process_correlation_id(data: dict):
    return data["unique_id"]


async def process_request(message: dict):
    return {'response': message["data"] * 2}


class BrokerServer:
    def __init__(self, bind_address: str):

        self.bind_address = bind_address
        self.context = zmq.asyncio.Context.instance()
        self.socket = self.context.socket(zmq.REP)
        self.running = False

    def connect(self):
        self.socket.bind(self.bind_address)

    async def start_listening(self):
        self.running = True
        while self.running:
            try:
                message = await self.socket.recv()
                await self.handle_request(message)
            except Exception as ex:
                print("Error in server:", ex)

    async def handle_request(self, message: bytes):
        try:
            data = json.loads(message.decode())
            correlation_id = data.get("correlation_id")
            payload = data.get("payload")
        except Exception as ex:
            print("Error parsing message:", ex)
            result = {"status": "error"}
            correlation_id = None
        else:
            result = await process_request(payload)
        response = {
            "correlation_id": correlation_id,
            "result": result
        }
        await self.socket.send(json.dumps(response).encode())

    async def close(self):
        self.running = False
        self.socket.close()
        self.context.term()


async def start_up_zeromq_server(bind_address: str) -> Tuple[BrokerServer, asyncio.Task]:
    rpc_server = BrokerServer(bind_address)
    rpc_server.connect()
    server_task = asyncio.create_task(rpc_server.start_listening())
    print("Broker Server initialized on", bind_address)
    return rpc_server, server_task
