from aiohttp import web

from tasks import _tasks


async def get_task(request: web.Request):
    task_id = int(request.query['id'])
    result = await _tasks.get_task(request.app.db, task_id)
    if result['status'] == 'ok':
        task = result['task']
        task['published'] = task['published'].isoformat()
        task['id'] = task.pop('_id')
        return web.json_response(result['task'])
    return web.json_response(
        {
            'reason': result['reason']
        },
        status=404
    )


async def get_proposed_task(request: web.Request):
    task_id = int(request.query['id'])
    result = await _tasks.get_proposed_task(request.app.db, task_id)
    if result['status'] == 'ok':
        task = result['task']
        task['proposed'] = task['proposed'].isoformat()
        task['id'] = task.pop('_id')
        return web.json_response({'task': result['task']})
    return web.json_response(
        {
            'reason': result['reason']
        },
        status=404
    )


async def publish_task(request: web.Request):
    data = await request.json()
    await _tasks.publish_task(
        request.app.db, **data
    )
    return web.json_response(
        {},
        status=201
    )


async def propose_task(request: web.Request):
    data = await request.json()
    result = await _tasks.propose_task(
        request.app.db, **data
    )
    return web.json_response(
        {'id': result['task_id']},
        status=201
    )


async def delete_proposed_task(request: web.Request):
    task_id = int(request.query['id'])
    result = await _tasks.delete_proposed_task(
        request.app.db, task_id
    )
    if result['status'] == 'ok':
        return web.json_response({})
    return web.json_response(
        {
            'reason': result['reason']
        },
        status=404
    )


async def update_proposed_task(request: web.Request):
    task_id = int(request.query['id'])
    data = await request.json()
    result = await _tasks.update_proposed_task(
        request.app.db, task_id, **data
    )
    if result['status'] == 'ok':
        return web.json_response({})
    return web.json_response(
        {
            'reason': result['reason']
        },
        status=404
    )


async def solve_task(request: web.Request):
    task_id = int(request.query['id'])
    result = await _tasks.solve(request.app.db, task_id)
    if result['status'] == 'ok':
        return web.json_response({})
    return web.json_response(
        {
            'reason': result['reason']
        },
        status=404
    )


async def search_tasks(request: web.Request):
    data = await request.json()
    result = await _tasks.search_tasks(
        request.app.db, **data
    )
    for task in result['tasks']:
        task['id'] = task.pop('_id')
    return web.json_response(
        {
            'tasks': result['tasks']
        }
    )


async def search_proposed_tasks(request: web.Request):
    data = await request.json()
    result = await _tasks.search_proposed_tasks(
        request.app.db, **data
    )
    for task in result['tasks']:
        task['id'] = task.pop('_id')
    return web.json_response(
        {
            'tasks': result['tasks']
        }
    )


async def count_tasks(request: web.Request):
    result = await _tasks.count_tasks(request.app.db)
    return web.json_response(
        {
            'count': result
        }
    )


async def count_proposed_tasks(request: web.Request):
    result = await _tasks.count_proposed_tasks(request.app.db)
    return web.json_response(
        {
            'count': result
        }
    )
