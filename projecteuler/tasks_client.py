import asyncio

from common import constants
from common import utils


class TasksClient:
    def __init__(self, loop=None):
        self.baseurl = 'http://localhost:{}'.format(constants.TASKS_PORT)
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

    async def search_tasks(self, **data):
        return await self._request(
            method='POST',
            url='/tasks/search',
            data=data,
        )

    async def search_proposed_tasks(self, **data):
        return await self._request(
            method='POST',
            url='/proposed_tasks/search',
            data=data,
        )

    async def count(self):
        return await self._request(
            method='GET',
            url='/tasks/count',
        )

    async def proposed_count(self):
        return await self._request(
            method='GET',
            url='/proposed_tasks/count',
        )

    async def get_task(self, task_id):
        return await self._request(
            method='GET',
            url='/tasks',
            params={'id': task_id},
        )

    async def get_proposed_task(self, task_id):
        return await self._request(
            method='GET',
            url='/proposed_tasks',
            params={'id': task_id},
        )

    async def solve(self, task_id):
        return await self._request(
            method='POST',
            url='/tasks/solve',
            params={'id': task_id},
        )

    async def propose(self, **data):
        return await self._request(
            method='POST',
            url='/proposed_tasks',
            data=data
        )

    async def publish(self, **data):
        return await self._request(
            method='POST',
            url='/tasks',
            data=data
        )

    async def update_proposed_task(self, task_id, **data):
        return await self._request(
            method='PATCH',
            url='/proposed_tasks',
            data=data,
            params={
                'id': task_id
            }
        )

    async def delete_proposed_task(self, task_id):
        return await self._request(
            method='DELETE',
            url='/proposed_tasks',
            params={
                'id': task_id
            }
        )
