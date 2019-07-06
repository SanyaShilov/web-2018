from motor import motor_asyncio


class Database:
    def __init__(self):
        client = motor_asyncio.AsyncIOMotorClient(
            host='mongodb://localhost:33333'
        )
        db = client.db

        self.users = db.users
        self.tasks = db.tasks
        self.proposed_tasks = db.proposed_tasks
