# pylint: disable=redefined-outer-name

import json

import bson
import pytest
from motor import motor_asyncio

import common.constants
import common.db
import common.utils
import projecteuler.app
import tasks.app
import users.app


PROJECTEULER_PORT = 9090
TASKS_PORT = 9091
USERS_PORT = 9092


def convert(obj):
    if isinstance(obj, dict):
        if '$oid' in obj:
            return bson.ObjectId(obj['$oid'])
        if '$date' in obj:
            return common.utils.parse_timestring(obj['$date'])
        return {
            key: convert(value) for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [convert(item) for item in obj]
    return obj


async def filldb(database, filename):
    file = open(filename)
    json_data = json.load(file)
    for key, value in json_data.items():
        await getattr(database, key).insert_many(convert(value))
    file.close()


@pytest.fixture(autouse=True)
async def db(monkeypatch, loop):
    client = motor_asyncio.AsyncIOMotorClient(io_loop=loop)
    db = client.test_db

    await db.users.drop()
    await db.tasks.drop()
    await db.proposed_tasks.drop()

    class Database:
        def __init__(self):
            self.users = db.users
            self.tasks = db.tasks
            self.proposed_tasks = db.proposed_tasks

    database = Database()

    monkeypatch.setattr(common.db, 'Database', Database)

    await filldb(database, './tests/database.json')

    return database


@pytest.fixture(autouse=True)
def utcnow(monkeypatch):
    from freezegun import freeze_time

    freezer = freeze_time("2018-11-14 23:09:01")
    freezer.start()
    yield
    freezer.stop()


@pytest.fixture()
def oid(monkeypatch):
    const_object_id = bson.ObjectId('5be1e9ea4b3e4d0db08713b7')

    def get_oid():
        return const_object_id

    monkeypatch.setattr(bson, 'ObjectId', get_oid)
    return const_object_id


@pytest.fixture()
def tasks_app():
    return tasks.app.TasksApp()


@pytest.fixture()
def users_app():
    return users.app.UsersApp()


@pytest.fixture()
def projecteuler_app():
    return projecteuler.app.ProjectEulerApp()


@pytest.fixture()
async def projecteuler_client(aiohttp_client, projecteuler_app, monkeypatch):
    monkeypatch.setattr(
        common.constants, 'PROJECTEULER_PORT', PROJECTEULER_PORT
    )
    client = await aiohttp_client(
        projecteuler_app, server_kwargs={'port': PROJECTEULER_PORT}
    )
    client.db = projecteuler_app.db
    return client


@pytest.fixture()
async def tasks_client(aiohttp_client, tasks_app, monkeypatch):
    monkeypatch.setattr(
        common.constants, 'TASKS_PORT', TASKS_PORT
    )
    client = await aiohttp_client(
        tasks_app, server_kwargs={'port': TASKS_PORT}
    )
    client.db = tasks_app.db
    return client


@pytest.fixture()
async def users_client(aiohttp_client, users_app, monkeypatch):
    monkeypatch.setattr(
        common.constants, 'USERS_PORT', USERS_PORT
    )
    client = await aiohttp_client(
        users_app, server_kwargs={'port': USERS_PORT}
    )
    client.db = users_app.db
    return client
