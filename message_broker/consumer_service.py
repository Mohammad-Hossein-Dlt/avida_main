import asyncio
import json
import aio_pika

from config.config import BROKER_URL


class BrokerClient:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.futures = {}

    async def connect(self):
        self.connection: aio_pika.abc.AbstractRobustConnection = await aio_pika.connect_robust(self.amqp_url)
        self.channel: aio_pika.abc.AbstractRobustChannel = await self.connection.channel()
        self.callback_queue: aio_pika.abc.AbstractRobustQueue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response, no_ack=True)

    def on_response(self, message: aio_pika.abc.AbstractIncomingMessage):
        correlation_id = message.correlation_id
        if correlation_id in self.futures:
            future = self.futures.pop(correlation_id)
            future.set_result(message.body)

    async def send_request(self, correlation_id: str, message: str, routing_key: str) -> str:
        future = asyncio.get_running_loop().create_future()
        self.futures[correlation_id] = future

        encoded_message = message.encode()

        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=encoded_message,
                reply_to=self.callback_queue.name,
                correlation_id=correlation_id,
            ),
            routing_key=routing_key,
        )

        response = await future
        return response.decode()

    async def close(self):
        if self.connection:
            await self.connection.close()


async def send_message_broker(correlation_id: str, payload: dict, queue_name: str) -> dict:
    rpc_client = BrokerClient(BROKER_URL)
    await rpc_client.connect()

    encode_payload = json.dumps(payload)
    response: str = await rpc_client.send_request(
        correlation_id=correlation_id,
        message=encode_payload,
        routing_key=queue_name,
    )
    await rpc_client.close()

    print(correlation_id, " ", response)

    try:
        response_decode = json.loads(response)
    except Exception as ex:
        print(ex)
        response_decode = {"status": "error"}

    return response_decode
