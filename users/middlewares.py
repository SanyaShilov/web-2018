import bson
from aiohttp import web

from common import constants


def token_required(func):
    async def handler(request, *args, **kwargs):
        request['token'] = request.headers.get(constants.USER_TOKEN_HEADER)
        if not request['token']:
            return web.json_response(
                {
                    'reason': 'no_token'
                },
                status=401
            )
        if not bson.ObjectId.is_valid(request['token']):
            return web.json_response(
                {
                    'reason': 'wrong_token'
                },
                status=401
            )
        request['user'] = await request.app.db.users.find_one(
            {
                'token': request['token']
            }
        )
        if not request['user']:
            return web.json_response(
                {
                    'reason': 'wrong_token'
                },
                status=401
            )
        return await func(request, *args, **kwargs)
    return handler


def admin_rights_required(func):
    async def handler(request, *args, **kwargs):
        if not request['user'].get('admin'):
            return web.json_response(
                {
                    'reason': 'not_admin'
                },
                status=403
            )
        return await func(request, *args, **kwargs)
    return handler
