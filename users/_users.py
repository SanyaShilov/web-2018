import datetime

import bson
import pymongo


async def register(db, login, password):
    token = str(bson.ObjectId())
    user = await db.users.find_one_and_update(
        {
            '$or': [
                {'login': login},
                {'password': password},
            ],
        },
        {
            '$setOnInsert': {
                'login': login,
                'password': password,
                'token': token,
                'solutions': [],
                'solutions_count': 0,
            },
        },
        upsert=True,
        return_document=True,
    )
    if user.get('token') == token:
        return {'status': 'ok', 'token': token}
    if user['login'] == login:
        return {'status': 'error', 'reason': 'login_exists'}
    return {'status': 'error', 'reason': 'password_exists'}


async def sign_in(db, login, password):
    user = await db.users.find_one(
        {
            'login': login,
        },
    )
    if not user:
        return {'status': 'error', 'reason': 'wrong_login'}
    if user['password'] != password:
        return {'status': 'error', 'reason': 'wrong_password'}
    if 'token' in user:
        return {'status': 'ok', 'token': user['token']}
    token = str(bson.ObjectId())
    await db.users.update_one(
        {
            '_id': user['_id']
        },
        {
            '$set': {
                'token': token,
            },
        },
    )
    return {'status': 'ok', 'token': token}


async def sign_out(db, user):
    await db.users.update_one(
        {
            '_id': user['_id']
        },
        {
            '$unset': {
                'token': True
            },
        },
    )
    return {'status': 'ok'}


async def change_info(db, user, **data):
    query = []
    if 'login' in data and user['login'] != data['login']:
        query.append({'login': data['login']})
    if 'password' in data and user['password'] != data['password']:
        query.append({'password': data['password']})
    if query:
        existing_user = await db.users.find_one(
            {
                '$or': query,
            }
        )
        if existing_user:
            if existing_user['login'] == data.get('login'):
                return {'status': 'error', 'reason': 'login_exists'}
            return {'status': 'error', 'reason': 'password_exists'}
    await db.users.update_one(
        {
            '_id': user['_id']
        },
        {
            '$set': data
        }
    )
    return {'status': 'ok'}


async def solve(db, user, task_id):
    result = await db.users.update_one(
        {
            '_id': user['_id'],
            'solutions.task_id': {
                '$ne': task_id,
            }
        },
        {
            '$push': {
                'solutions': {
                    'task_id': task_id,
                    'submitted': datetime.datetime.utcnow()
                }
            },
            '$inc': {
                'solutions_count': 1
            }
        }
    )
    if not result.matched_count:
        return {'status': 'error', 'reason': 'task_id_exists'}
    return {'status': 'ok'}


async def mark_propose(db, user, task_id):
    await db.users.update_one(
        {
            '_id': user['_id']
        },
        {
            '$set': {
                'proposed_task_id': task_id
            }
        }
    )
    return {'status': 'ok'}


async def unmark_propose(db, task_id):
    await db.users.update_one(
        {
            'proposed_task_id': task_id
        },
        {
            '$unset': {
                'proposed_task_id': True
            }
        }
    )
    return {'status': 'ok'}


async def statistics(db, detailed=None):
    common_statistics = {}
    cursor = db.users.aggregate([
        {
            '$group': {
                '_id': None,
                'users': {'$sum': 1},
                '_countries': {
                    '$addToSet': '$country'
                },
                '_programming_languages': {
                    '$addToSet': '$programming_language'
                },
                'total_solutions': {'$sum': '$solutions_count'},
                'average_solutions': {'$avg': '$solutions_count'}
            }
        },
        {
            '$addFields':{
                'countries': {'$size': {
                    '$setDifference': ['$_countries', ['', None]]
                }},
                'programming_languages': {'$size': {
                    '$setDifference': ['$_programming_languages', ['', None]]
                }},
            }
        },
        {
            '$project': {
                '_id': False,
                '_countries': False,
                '_programming_languages': False,
            },

        }
    ])
    async for item in cursor:
        common_statistics = item
    detailed_statistics = {}
    if detailed == 'countries':
        detailed_statistics['detailed_countries'] = await db.users.aggregate([
            {
                '$match': {
                    'country': {
                        '$exists': True,
                        '$ne': '',
                    }
                }
            },
            {
                '$group': {
                    '_id': '$country',
                    'users': {'$sum': 1},
                    'average_solutions': {'$avg': '$solutions_count'}
                }
            },
            {
                '$addFields': {
                    'country': '$_id'
                }
            },
            {
                '$project': {
                    '_id': False,
                },
            },
            {
                '$sort': bson.SON([
                    ('country', pymongo.ASCENDING),
                ]),
            },
        ]).to_list(None)
    elif detailed == 'programming_languages':
        detailed_statistics['detailed_programming_languages'] = (
            await db.users.aggregate([
                {
                    '$match': {
                        'programming_language': {
                            '$exists': True,
                            '$ne': '',
                        }
                    }
                },
                {
                    '$group': {
                        '_id': '$programming_language',
                        'users': {'$sum': 1},
                        'average_solutions': {'$avg': '$solutions_count'}
                    }
                },
                {
                    '$addFields': {
                        'programming_language': '$_id'
                    }
                },
                {
                    '$project': {
                        '_id': False,
                    },
                },
                {
                    '$sort': bson.SON([
                        ('programming_language', pymongo.ASCENDING),
                    ]),
                }
            ]).to_list(None)
        )
    elif detailed == 'solutions':
        detailed_statistics['detailed_solutions'] = await db.users.aggregate([
            {
                '$group': {
                    '_id': '$solutions_count',
                    'users_solved_exactly': {'$sum': 1},
                }
            },
            {
                '$lookup': {
                    'from': 'users',
                    'localField': '_',
                    'foreignField': '_',
                    'as': 'lookuped'
                }
            },
            {
                '$unwind': '$lookuped'
            },
            {
                '$group': {
                    '_id': '$_id',
                    'users_solved_exactly': {'$min': '$users_solved_exactly'},
                    'users_solved_at_least': {
                        '$sum': {
                            '$cond': {
                                'if': {
                                    '$gte': [
                                        '$lookuped.solutions_count',
                                        '$_id'
                                    ]
                                },
                                'then': 1,
                                'else': 0
                            }
                        }
                    },
                }
            },
            {
                '$addFields': {
                    'number_of_tasks': '$_id'
                }
            },
            {
                '$project': {
                    '_id': False,
                },
            },
            {
                '$sort': bson.SON([
                    ('number_of_tasks', pymongo.ASCENDING),
                ]),
            }
        ]).to_list(None)
    common_statistics.update(detailed_statistics)
    return common_statistics
