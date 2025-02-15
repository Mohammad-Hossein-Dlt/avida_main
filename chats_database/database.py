from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from chats_database.models import ChatSession


async def init_chats_db():
    client = AsyncIOMotorClient(
        "mongodb://root:NBIfQTp5U0i0NoCHveTYXcH1@logan.liara.cloud:30821/my-app?authSource=admin",
    )
    await init_beanie(database=client["Chats"], document_models=[ChatSession])

    print("Chats database inited.")
