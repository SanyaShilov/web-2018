from aiohttp import web

from common import utils
from projecteuler import exceptions

@web.middleware
async def authenticate(request: web.Request, handler):
    request['user'] = None
    if utils.startswith_one(request.rel_url, [
            '/home/sanyash/bootstrap', '/projecteuler/static'
    ]):
        return await handler(request)
    request['token'] = request.cookies.get('projecteuler-user-token')
    if request['token']:
        response = await request.app.users_client.me(request['token'])
        request['user'] = response.get('user')
    return await handler(request)


@web.middleware
async def redirect(request: web.Request, handler):
    url = str(request.rel_url)
    about = web.Response(
        status=303,
        headers={
            'Location': '/about'
        }
    )
    if utils.startswith_one(url, [
            '/about'
    ]):
        return await handler(request)
    if request['user']:
        if utils.startswith_one(url, [
                '/sign_in', '/register',
        ]):
            return about
    else:
        if utils.startswith_one(url, [
                '/sign_out', '/account',
        ]):
            return about
    try:
        return await handler(request)
    except exceptions.NeedRedirection:
        return web.Response(
            status=303,
            headers={
                'Location': request.path,
            }
        )
