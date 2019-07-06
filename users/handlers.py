from aiohttp import web

from users import _users
from users import middlewares


@middlewares.token_required
async def me(request):  # pylint: disable=invalid-name
    request['user'].pop('_id')
    request['user'].pop('token')
    for solution in request['user']['solutions']:
        solution['submitted'] = solution['submitted'].isoformat()
    return web.json_response({'user': request['user']})


@middlewares.token_required
async def change_info(request):
    data = await request.json()
    result = await _users.change_info(
        request.app.db, request['user'], **data
    )
    if result['status'] == 'ok':
        return web.json_response({})
    return web.json_response(
        {
            'reason': result['reason']
        },
        status=422
    )


async def register(request: web.Request):
    data = await request.json()
    result = await _users.register(
        request.app.db, data['login'], data['password']
    )
    if result['status'] == 'ok':
        return web.json_response(
            {
                'token': result['token'],
            },
            status=201
        )
    return web.json_response(
        {
            'reason': result['reason'],
        },
        status=422,
    )


async def sign_in(request: web.Request):
    data = await request.json()
    result = await _users.sign_in(
        request.app.db, data['login'], data['password']
    )
    if result['status'] == 'ok':
        return web.json_response(
            {
                'token': result['token'],
            },
        )
    return web.json_response(
        {
            'reason': result['reason'],
        },
        status=403,
    )


@middlewares.token_required
async def sign_out(request):
    await _users.sign_out(
        request.app.db, request['user']
    )
    return web.json_response({})


@middlewares.token_required
async def solve(request):
    data = await request.json()
    result = await _users.solve(
        request.app.db, request['user'], data['task_id']
    )
    if result['status'] == 'ok':
        return web.json_response({})
    return web.json_response(
        {
            'reason': result['reason']
        },
        status=422
    )


@middlewares.token_required
async def mark_propose(request):
    data = await request.json()
    await _users.mark_propose(
        request.app.db, request['user'], data['task_id']
    )
    return web.json_response({})


@middlewares.token_required
@middlewares.admin_rights_required
async def unmark_propose(request):
    data = await request.json()
    await _users.unmark_propose(
        request.app.db, data['task_id']
    )
    return web.json_response({})


async def statistics(request: web.Request):
    detailed = request.query.get('detailed')
    return web.json_response(
        {
            'statistics': await _users.statistics(request.app.db, detailed)
        }
    )
