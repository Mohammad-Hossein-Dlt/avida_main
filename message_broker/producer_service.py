import asyncio
import json
from asyncio import Task
import aio_pika
from typing import Tuple

from config.config import BROKER_URL


class BrokerServer:
    def __init__(self, amqp_url: str, queue_name: str):
        self.amqp_url = amqp_url
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self) -> str:
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(name=self.queue_name, durable=True, auto_delete=True)
        return self.queue.name

    async def start_listening(self):
        async with self.connection:
            await self.queue.consume(callback=self.handle_request)
            await asyncio.Future()

    async def handle_request(self, message: aio_pika.abc.AbstractIncomingMessage):
        async with message.process():

            try:
                request_data = json.loads(message.body.decode())
                # request_correlation_id = json.loads(message.correlation_id)
            except Exception as ex:
                print(ex)
                result = {"status": "error"}
                # id_result = {"status": "error"}
            else:
                result = await process_request(request_data)
                # id_result = await process_correlation_id(request_correlation_id)

            encode_result = json.dumps(result)
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=str(encode_result).encode(),
                    correlation_id=message.correlation_id
                ),
                routing_key=message.reply_to
            )

    async def close(self):
        if self.connection:
            await self.connection.close()


async def process_correlation_id(data: dict):
    return data["unique_id"]


async def process_request(message: dict):
    return {'response': message["data"] * 2}


async def start_up_broker_server(queue_name: str) -> Tuple[BrokerServer, str, Task]:
    rpc_server = BrokerServer(BROKER_URL, queue_name=queue_name)
    queue_name = await rpc_server.connect()
    server_task = asyncio.create_task(rpc_server.start_listening())
    print("Broker inited")
    return rpc_server, queue_name, server_task
