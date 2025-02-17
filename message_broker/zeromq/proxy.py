# import asyncio
# import zmq
#
#
# class ZMQProxy:
#     def __init__(self):
#         self.context = zmq.Context()
#
#         self.backend_socket = self.context.socket(zmq.DEALER)
#         self.backend_port = None
#
#         self.frontend_socket = self.context.socket(zmq.ROUTER)
#         self.frontend_port = None
#
#         self.running = False
#
#     def connect_backend(self):
#         self.backend_socket.bind("tcp://0.0.0.0:1234")
#         self.backend_port = self.backend_socket.getsockopt_string(zmq.LAST_ENDPOINT)
#
#     def connect_frontend(self):
#         self.frontend_socket.bind("tcp://0.0.0.0:12345")
#         self.frontend_port = self.frontend_socket.getsockopt_string(zmq.LAST_ENDPOINT)
#
#     async def start(self):
#         print(f"Frontend bound to: {self.frontend_port}")
#         print(f"Backend bound to: {self.backend_port}")
#         print("Proxy started...")
#
#         poller = zmq.Poller()
#         poller.register(self.frontend_socket, zmq.POLLIN)
#         poller.register(self.backend_socket, zmq.POLLIN)
#
#         self.running = True
#
#         while self.running:
#             # Wait for an event on either socket
#             events = dict(poller.poll(1000))
#
#             # If there's a message from a client on the frontend:
#             if self.frontend_socket in events and events[self.frontend_socket] == zmq.POLLIN:
#                 # A ROUTER socket receives messages in multipart form:
#                 message = self.frontend_socket.recv_multipart()
#                 print("Received from client:", message)
#                 # You can add custom processing of the message here.
#                 # Forward the message to the backend (worker side)
#                 self.backend_socket.send_multipart(message)
#
#             # If there's a message from a worker on the backend:
#             if self.backend_socket in events and events[self.backend_socket] == zmq.POLLIN:
#                 message = self.backend_socket.recv_multipart()
#                 print("Received from worker:", message)
#                 # You can modify or log the response here before forwarding.
#                 # Forward the message back to the client via the frontend
#                 self.frontend_socket.send_multipart(message)
#
#     def close_socket(self):
#         self.running = False
#         self.frontend_socket.close()
#         self.backend_socket.close()
#         self.context.term()
#         print("Proxy stopped.")
#
#
# async def start_proxy_task():
#     proxy = ZMQProxy()
#     proxy.connect_backend()
#     proxy.connect_frontend()
#     start_task = asyncio.create_task(proxy.start())
#     return start_task, proxy


# import zmq
# import asyncio
# import sys
#
# if sys.platform.startswith('win'):
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#
#
# # پروکسی: برای دریافت درخواست از کلاینت و ارسال به سرور و بالعکس
# def proxy():
#     context = zmq.Context()
#
#     frontend = context.socket(zmq.ROUTER)
#     frontend.bind("tcp://localhost:5555")  # پورت برای دریافت درخواست‌ها از کلاینت
#
#     backend = context.socket(zmq.DEALER)
#     backend.bind("tcp://localhost:5556")  # پورت برای ارسال درخواست‌ها به سرور
#
#     # Create a Poller to manage incoming events on both sockets
#     poller = zmq.Poller()
#     poller.register(frontend, zmq.POLLIN)
#     poller.register(backend, zmq.POLLIN)
#
#     print("Proxy started...")
#     # zmq.proxy_steerable(frontend, backend)
#
#     while True:
#         # Wait for an event on either socket
#         events = dict(poller.poll())
#
#         # If there's a message from a client on the frontend:
#         if frontend in events and events[frontend] == zmq.POLLIN:
#             # A ROUTER socket receives messages in multipart form:
#             message = frontend.recv_multipart()
#             print("Received from client:", message)
#             # You can add custom processing of the message here.
#             # Forward the message to the backend (worker side)
#             backend.send_multipart(message)
#
#         # If there's a message from a worker on the backend:
#         if backend in events and events[backend] == zmq.POLLIN:
#             message = backend.recv_multipart()
#             print("Received from worker:", message)
#             # You can modify or log the response here before forwarding.
#             # Forward the message back to the client via the frontend
#             frontend.send_multipart(message)
#
#     # frontend.close()
#     # backend.close()
#     # context.term()
#
#
# # سرور: برای دریافت درخواست از پروکسی و ارسال پاسخ
# async def start_server():
#     context = zmq.Context()
#     server = context.socket(zmq.REP)
#     server.connect("tcp://localhost:5556")  # اتصال به پروکسی
#
#     while True:
#         request = server.recv_string()
#         print(f"Server received: {request}")
#         await asyncio.sleep(1)  # شبیه‌سازی پردازش درخواست
#         await server.send_string(f"Reply to {request}")
#
#
# # کلاینت: برای ارسال درخواست به پروکسی و دریافت پاسخ
# async def start_client():
#     context = zmq.Context()
#     client = context.socket(zmq.REQ)
#     client.connect("tcp://localhost:5555")  # اتصال به پروکسی
#
#     for i in range(5):
#         message = f"Request {i}"
#         await client.send_string(message)
#         response = client.recv_string()
#         print(f"Client received: {response}")
#
#
# async def main():
#     # threading.Thread(target=proxy).start()
#     proxy_task = asyncio.to_thread(proxy)
#     server_task = asyncio.create_task(start_server())
#     client_task = asyncio.create_task(start_client())
#
#     await proxy_task
#     await client_task
#     await server_task
#
#
# if __name__ == "__main__":
#     # اجرای حلقه همزمان asyncio
#     asyncio.run(main())


import zmq
import zmq.asyncio
import asyncio
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

context = zmq.asyncio.Context()


# پروکسی: پیام‌ها را از کلاینت به سرور و از سرور به کلاینت ارسال می‌کند
async def proxy():
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://localhost:5555")  # پروکسی درخواست را از کلاینت دریافت می‌کند

    backend = context.socket(zmq.DEALER)
    backend.bind("tcp://localhost:5556")  # پروکسی درخواست را به سرور ارسال می‌کند

    print("Proxy started...")

    while True:
        tasks = [
            frontend.recv_multipart(),
            backend.recv_multipart()
        ]
        print(0)

        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            message = task.result()

            if task == tasks[0]:  # پیام از کلاینت آمده
                await backend.send_multipart(message)
            else:  # پیام از سرور آمده
                await frontend.send_multipart(message)


# سرور: درخواست‌ها را پردازش کرده و پاسخ را ارسال می‌کند
async def start_server():
    server = context.socket(zmq.REP)
    server.connect("tcp://localhost:5556")  # اتصال به پروکسی

    while True:
        request = await server.recv_string()
        print(f"Server received: {request}")

        await server.send_string(f"Reply to {request}")


# کلاینت: درخواست‌ها را ارسال و پاسخ‌ها را دریافت می‌کند
async def start_client():
    client = context.socket(zmq.REQ)
    client.connect("tcp://localhost:5555")  # اتصال به پروکسی

    for i in range(5):
        message = f"Request {i}"
        await client.send_string(message)
        response = await client.recv_string()
        print(f"Client received: {response}")


async def main():
    proxy_task = asyncio.create_task(proxy())
    server_task = asyncio.create_task(start_server())
    client_task = asyncio.create_task(start_client())

    # await proxy_task
    # await server_task
    await client_task

    proxy_task.cancel()
    server_task.cancel()
    client_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
