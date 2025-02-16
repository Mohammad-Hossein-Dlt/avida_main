import asyncio
import json
import uuid
from asyncio import Task
from datetime import datetime
import pytz
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from main_database.database import sessionLocal
from main_database.models import UserTemp
from main_database.database import check_database, engine
from main_database.models import Base
from message_broker.holder import QueueNameHolder
from message_broker.producer_service import start_up_broker_server
from message_broker.consumer_service import send_message_broker
from message_broker.zeromq.server import start_up_zeromq_server
from message_broker.zeromq.client import send_message_zeromq
from chats_database.database import init_chats_db
from routers.admin import assistant
from routers.general import verify_phone
from routers.user import authentication
from routers.chat import chatting
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def delete_users_temps():
    db = sessionLocal()

    time_now = datetime.now(pytz.UTC)

    junk_user_temps = db.query(UserTemp).where(
        UserTemp.ExpirationDate < time_now
    ).all()

    for i in junk_user_temps:
        db.delete(i)

    db.commit()
    db.close()


async def do_update():
    while True:
        delete_users_temps()
        await asyncio.sleep(1)


def start_update() -> Task:
    start_task = asyncio.create_task(do_update())
    print("Start update.")
    return start_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Start up.")

    check_database()
    Base.metadata.create_all(bind=engine)

    await init_chats_db()

    rpc_server, queue_name, server_task = await start_up_broker_server("queue_name")
    QueueNameHolder.queue_name = queue_name

    zeromq_server, zeromq_task = await start_up_zeromq_server('tcp://0.0.0.0:1234')

    update_task = start_update()

    yield

    await rpc_server.close()
    server_task.cancel()

    await zeromq_server.close()
    zeromq_task.cancel()

    update_task.cancel()

    print("Shout down.")


app = FastAPI(lifespan=lifespan)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.title = "Avida"
BASE_URL = "/api/v1"

app.include_router(assistant.router, prefix=BASE_URL)
app.include_router(verify_phone.router, prefix=BASE_URL)
app.include_router(authentication.router, prefix=BASE_URL)
app.include_router(chatting.router, prefix=BASE_URL)


@app.post("/send_message")
async def send_message(request: Request, message: dict):
    correlation_id = {"user_id": 1, "unique_id": uuid.uuid4().hex}

    encode_id = json.dumps(correlation_id)

    # response = await send_message_broker(
    #     correlation_id=encode_id,
    #     payload=message,
    #     queue_name=QueueNameHolder.queue_name,
    # )

    response = await send_message_zeromq(encode_id, message, 'tcp://82.115.19.115:1234')

    client_ip = request.client.host

    forwarded_ip = request.headers.get("X-Forwarded-For")

    return {
        "r": response,
        "ip": client_ip,
        "forwarded_ip": forwarded_ip,
    }

# TOTAL_REQUESTS = 1_000_000
#
#
# async def client():
#     ctx = zmq.asyncio.Context.instance()
#     ctx1 = zmq.asyncio.Context.instance()
#
#     send_socket = ctx.socket(zmq.REQ)
#     send_socket.connect("tcp://localhost:1234")
#
#     receive_socket = ctx1.socket(zmq.REP)
#     receive_socket.bind("tcp://localhost:1234")
#
#     time.sleep(1)
#
#     async def send_messages():
#         for i in range(TOTAL_REQUESTS):
#             print(i)
#             await send_socket.send(f"Message {i}".encode())
#             res = await send_socket.recv()
#
#     async def receive_messages():
#
#         x = 0
#
#         while x < TOTAL_REQUESTS:
#             try:
#                 reply = await receive_socket.recv()
#                 await receive_socket.send('Test'.encode())
#                 print(reply.decode())
#             except Exception as ex:
#                 print("Error in server:", ex)
#
#             x += 1
#
#     send_task = asyncio.create_task(send_messages())
#     recv_task = asyncio.create_task(receive_messages())
#
#     await asyncio.gather(send_task, recv_task)
#
#
# if __name__ == "__main__":
#     asyncio.run(client())


