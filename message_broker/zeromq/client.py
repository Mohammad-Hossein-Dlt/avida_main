import json
import zmq.asyncio


class BrokerClient:
    def __init__(self, connect_address: str):

        self.connect_address = connect_address
        self.context = zmq.asyncio.Context.instance()
        self.socket = self.context.socket(zmq.REQ)

    def connect(self):
        self.socket.connect(self.connect_address)

    async def send_request(self, correlation_id: str, payload: dict) -> str:
        request = {
            "correlation_id": correlation_id,
            "payload": payload
        }
        await self.socket.send(json.dumps(request).encode())
        response = await self.socket.recv()

        return response.decode()

    def close_socket(self):
        self.socket.close()


async def send_message_zeromq(correlation_id: str, payload: dict, server_address: str) -> dict:

    rpc_client = BrokerClient(server_address)
    rpc_client.connect()

    response: str = await rpc_client.send_request(correlation_id, payload)
    rpc_client.close_socket()

    try:
        response_decode = json.loads(response)
    except Exception as ex:
        print("Error decoding response:", ex)
        response_decode = {"status": "error"}

    print(response)

    return response_decode
