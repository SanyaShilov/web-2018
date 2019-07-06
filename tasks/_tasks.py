import datetime

import bson
import pymongo


async def count_tasks(db):
    return await db.tasks.count_documents({})


async def count_proposed_tasks(db):
    return await db.proposed_tasks.count_documents({})


async def next_task_id(db):
    async for item in db.tasks.aggregate([
            {
                '$group': {
                    '_id': None,
                    'id': {'$max': '$_id'}
                }
            }
    ]):
        return item['id'] + 1
    return 1


async def next_proposed_task_id(db):
    async for item in db.proposed_tasks.aggregate([
            {
                '$group': {
                    '_id': None,
                    'id': {'$max': '$_id'}
                }
            }
    ]):
        return item['id'] + 1
    return 1


async def get_task(db, task_id):
    task = await db.tasks.find_one(
        {
            '_id': task_id
        }
    )
    if task:
        return {'status': 'ok', 'task': task}
    return {'status': 'error', 'reason': 'not_found'}


async def get_proposed_task(db, task_id):
    task = await db.proposed_tasks.find_one(
        {
            '_id': task_id
        }
    )
    if task:
        return {'status': 'ok', 'task': task}
    return {'status': 'error', 'reason': 'not_found'}


async def publish_task(db, title, text, answer, difficulty):
    while True:
        task_id = await next_task_id(db)
        now = datetime.datetime.utcnow().replace(microsecond=0)
        result = await db.tasks.update_one(
            {
                '_id': task_id,
            },
            {
                '$setOnInsert': {
                    'title': title,
                    'text': text,
                    'answer': answer,
                    'difficulty': difficulty,
                    'solved_by': 0,
                    'published': now
                }
            },
            upsert=True
        )
        if result.upserted_id:
            return {'status': 'ok'}


async def propose_task(db, title, text, answer, difficulty):
    while True:
        task_id = await next_proposed_task_id(db)
        now = datetime.datetime.utcnow().replace(microsecond=0)
        result = await db.proposed_tasks.update_one(
            {
                '_id': task_id,
            },
            {
                '$setOnInsert': {
                    'title': title,
                    'text': text,
                    'answer': answer,
                    'difficulty': difficulty,
                    'proposed': now
                }
            },
            upsert=True
        )
        if result.upserted_id:
            return {'status': 'ok', 'task_id': result.upserted_id}


async def delete_proposed_task(db, task_id):
    result = await db.proposed_tasks.delete_one(
        {
            '_id': task_id
        }
    )
    if result.deleted_count:
        return {'status': 'ok'}
    return {'status': 'error', 'reason': 'not_found'}


async def solve(db, task_id):
    result = await db.tasks.update_one(
        {
            '_id': task_id
        },
        {
            '$inc': {
                'solved_by': 1
            }
        }
    )
    if result.matched_count:
        return {'status': 'ok'}
    return {'status': 'error', 'reason': 'not_found'}


async def search_tasks(db, sort_by='id', sort_order='asc', offset=None,
                       limit=None, solved_ids=None, solved='all'):
    if sort_by == 'id':
        sort_by = '_id'
    if sort_order == 'asc':
        sort_order = pymongo.ASCENDING
    else:
        sort_order = pymongo.DESCENDING
    solved_ids = solved_ids or []
    pipeline = []
    if solved == 'yes':
        pipeline.append({
            '$match': {
                '_id': {'$in': solved_ids}
            }
        })
    elif solved == 'no':
        pipeline.append({
            '$match': {
                '_id': {'$nin': solved_ids}
            }
        })
    pipeline.extend([
        {
            '$project': {
                'title': '$title',
                'difficulty': '$difficulty',
                'solved_by': '$solved_by'
            }
        },
        {
            '$sort': bson.SON([
                (sort_by, sort_order)
            ])
        },
    ])
    if offset:
        pipeline.append({'$skip': offset})
    if limit:
        pipeline.append({'$limit': limit})
    cursor = db.tasks.aggregate(pipeline)
    tasks = []
    async for task in cursor:
        tasks.append(task)
    return {'status': 'ok', 'tasks': tasks}


async def search_proposed_tasks(db, sort_by='id', sort_order='asc',
                                offset=None, limit=None):
    if sort_by == 'id':
        sort_by = '_id'
    if sort_order == 'asc':
        sort_order = pymongo.ASCENDING
    else:
        sort_order = pymongo.DESCENDING
    pipeline = [
        {
            '$project': {
                'title': '$title',
                'difficulty': '$difficulty',
                'solved_by': '$solved_by'
            }
        },
        {
            '$sort': bson.SON([
                (sort_by, sort_order)
            ])
        },
    ]
    if offset:
        pipeline.append({'$skip': offset})
    if limit:
        pipeline.append({'$limit': limit})
    cursor = db.proposed_tasks.aggregate(pipeline)
    tasks = []
    async for task in cursor:
        tasks.append(task)
    return {'status': 'ok', 'tasks': tasks}


async def update_proposed_task(db, task_id, **data):
    result = await db.proposed_tasks.update_one(
        {
            '_id': task_id
        },
        {
            '$set': data
        }
    )
    if not result.matched_count:
        return {'status': 'error', 'reason': 'not_found'}
    return {'status': 'ok'}
