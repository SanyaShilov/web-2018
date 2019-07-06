# pylint: disable=broad-except

from aiohttp import web


async def register(request: web.Request):
    data = await request.post()
    token = None
    users_response = await request.app.users_client.register(
        data['login'], data['password']
    )
    if 'token' in users_response:
        token = users_response['token']
    if token:
        response = web.Response(
            status=303,
            headers={
                'Location': '/about'
            }
        )
        response.set_cookie('projecteuler-user-token', token)
        return response
    return web.Response(
        status=303,
        headers={
            'Location': '/register'
        }
    )


async def sign_in(request: web.Request):
    data = await request.post()
    users_response = await request.app.users_client.sign_in(
        data['login'], data['password']
    )
    token = users_response.get('token')
    if token:
        response = web.Response(
            status=303,
            headers={
                'Location': '/about'
            }
        )
        response.set_cookie('projecteuler-user-token', token)
        return response
    return web.Response(
        status=303,
        headers={
            'Location': '/sign_in'
        }
    )


async def change_info(request: web.Request):
    data = dict(await request.post())
    response = web.Response(
        status=303,
        headers={
            'Location': '/account'
        }
    )
    if 'confirm_password' in data:
        if data['password'] != data['confirm_password']:
            return response
        data.pop('confirm_password')
    await request.app.users_client.change_info(
        request['token'], **data
    )
    return response


async def sign_out(request: web.Request):
    response = web.Response(
        status=303,
        headers={
            'Location': '/about'
        }
    )
    await request.app.users_client.sign_out(request['token'])
    response.del_cookie('projecteuler-user-token')
    return response


async def submit_answer(request: web.Request):
    data = await request.post()
    task = await request.app.tasks_client.get_task(data['id'])
    if data['answer'] == task['answer']:
        await request.app.users_client.solve(request['token'], task['id'])
        await request.app.tasks_client.solve(task['id'])
    return web.Response(
        status=303,
        headers={
            'Location': '/task?id={}'.format(task['id'])
        }
    )


async def propose(request: web.Request):
    data = dict(await request.post())
    data['difficulty'] = int(data['difficulty'])
    if 'id' in data:
        task_id = int(data.pop('id'))
        await request.app.tasks_client.update_proposed_task(task_id, **data)
    else:
        tasks_response = await request.app.tasks_client.propose(**data)
        task_id = tasks_response['id']
        await request.app.users_client.mark_propose(request['token'], task_id)
    return web.Response(
        status=303,
        headers={
            'Location': '/propose'
        }
    )


async def reject(request: web.Request):
    data = dict(await request.post())
    task_id = int(data['id'])
    await request.app.tasks_client.delete_proposed_task(task_id)
    await request.app.users_client.unmark_propose(request['token'], task_id)
    return web.Response(
        status=303,
        headers={
            'Location': '/proposed_archives'
        }
    )


async def publish(request: web.Request):
    data = dict(await request.post())
    task_id = int(data.pop('id'))
    data['difficulty'] = int(data['difficulty'])
    await request.app.tasks_client.publish(**data)
    await request.app.tasks_client.delete_proposed_task(task_id)
    await request.app.users_client.unmark_propose(request['token'], task_id)
    return web.Response(
        status=303,
        headers={
            'Location': '/proposed_archives'
        }
    )


async def publish_yourself(request: web.Request):
    data = dict(await request.post())
    data['difficulty'] = int(data['difficulty'])
    await request.app.tasks_client.publish(**data)
    return web.Response(
        status=303,
        headers={
            'Location': '/proposed_archives'
        }
    )
