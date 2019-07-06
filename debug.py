#!/usr/bin/python3.6

import asyncio
import random
import string

from common import db as db_module
from common import constants
from users import _users
from tasks import _tasks


LOOP = asyncio.get_event_loop()


def random_string():
    return ''.join(
        (random.choice(string.ascii_letters)
         for _ in range(random.randint(5, 15)))
    )


async def filldb(db):
    await db.tasks.delete_many({})
    await db.users.delete_many({})
    for i in range(1, 51):
        file = open('/home/sanyash/tasks/task{}.txt'.format(i))
        lines = file.readlines()
        title, answer, *text = lines
        title = title.replace('\n', '')
        answer = answer.replace('\n', '')
        text = ''.join(text)
        await _tasks.publish_task(
            db,
            title=title, text=text, answer=answer,
            difficulty=random.randint(10, 100)
        )
    logins = set()
    while len(logins) < 999:
        logins.add(random_string())
    passwords = set()
    while len(passwords) < 999:
        passwords.add(random_string())
    for login, password in (
            list(zip(logins, passwords)) +
            [('sanyash', 'nyash_myash')]
    ):
        result = await _users.register(db, login, password)
        token = result['token']
        user = await db.users.find_one({'token': token})
        await _users.change_info(
            db, user,
            country=random.choice(constants.COUNTRIES),
            programming_language=random.choice(constants.PROGRAMMING_LANGUAGES)
        )
        task_ids = [n for n in range(1, 51)]
        random.shuffle(task_ids)
        for task_id in task_ids[:random.randint(0, 50)]:
            await _users.solve(db, user, task_id)
            await _tasks.solve(db, task_id)


async def main():
    db = db_module.Database()
    await filldb(db)
    await db.users.find_one_and_update(
        {
            'login': 'sanyash'
        },
        {
            '$set': {
                'admin': True
            }
        }
    )


if __name__ == '__main__':
    LOOP.run_until_complete(main())
