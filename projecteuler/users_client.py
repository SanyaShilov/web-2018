import asyncio

from common import constants
from common import utils


class UsersClient:
    def __init__(self, loop=None):
        self.baseurl = 'http://localhost:{}'.format(constants.USERS_PORT)
        self.session = asyncio.get_event_loop().run_until_complete(
            utils.create_session(loop)
        )

    async def _request(self, method, url,
                       params=None, data=None, headers=None):
        headers = headers or {}
        headers['Content-Type'] = 'application/json'
        response = await self.session.request(
            method=method,
            url=self.baseurl + url,
            params=params,
            json=data,
            headers=headers,
        )
        return await response.json()

    # pylint: disable=invalid-name
    async def me(self, token):
        return await self._request(
            method='GET',
            url='/me',
            headers={
                'projecteuler-user-token': token
            }
        )

    async def sign_out(self, token):
        return await self._request(
            method='POST',
            url='/sign_out',
            headers={
                'projecteuler-user-token': token
            }
        )

    async def sign_in(self, login, password):
        return await self._request(
            method='POST',
            url='/sign_in',
            data={
                'login': login,
                'password': password,
            },
        )

    async def register(self, login, password):
        return await self._request(
            method='POST',
            url='/register',
            data={
                'login': login,
                'password': password,
            },
        )

    async def change_info(self, token, **data):
        return await self._request(
            method='POST',
            url='/change_info',
            data=data,
            headers={
                'projecteuler-user-token': token
            }
        )

    async def solve(self, token, task_id):
        return await self._request(
            method='POST',
            url='/solve',
            data={
                'task_id': task_id,
            },
            headers={
                'projecteuler-user-token': token
            }
        )

    async def mark_propose(self, token, task_id):
        return await self._request(
            method='POST',
            url='/propose',
            data={
                'task_id': task_id
            },
            headers={
                'projecteuler-user-token': token
            }
        )

    async def unmark_propose(self, token, task_id):
        return await self._request(
            method='DELETE',
            url='/propose',
            data={
                'task_id': task_id
            },
            headers={
                'projecteuler-user-token': token
            }
        )

    async def statistics(self, detailed=None):
        params = {'detailed': detailed} if detailed else None
        return await self._request(
            method='GET',
            url='/statistics',
            params=params
        )
