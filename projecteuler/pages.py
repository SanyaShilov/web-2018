# pylint: disable=redefined-outer-name

from aiohttp import web
import aiohttp_jinja2

import common.constants
from projecteuler import constants
from projecteuler import utils


def prepare_text(text):
    return text.replace('\n', '<br>')


@aiohttp_jinja2.template('about.html')
async def about(request: web.Request):
    return {'user': request['user']}


@aiohttp_jinja2.template('register.html')
async def register(request: web.Request):
    return {'user': request['user']}


@aiohttp_jinja2.template('sign_in.html')
async def sign_in(request: web.Request):
    return {'user': request['user']}


@aiohttp_jinja2.template('account.html')
async def account(request: web.Request):
    return {
        'user': request['user'],
        'countries': common.constants.COUNTRIES,
        'programming_languages': common.constants.PROGRAMMING_LANGUAGES
    }


@aiohttp_jinja2.template('statistics.html')
async def statistics(request: web.Request):
    detailed = request.query.get('detailed')
    statistics = await request.app.users_client.statistics(detailed)
    statistics = utils.round_statistics(statistics)
    return {'user': request['user'], 'statistics': statistics['statistics']}


@aiohttp_jinja2.template('archives.html')
async def archives(request: web.Request):
    user = request['user']
    sort_by = request.query.get('sort_by', 'id')
    sort_order = request.query.get('sort_order', 'asc')
    page = int(request.query.get('page', 1))
    solved = request.query.get('solved', 'all') if user else 'all'
    solved_ids = [
        solution['task_id'] for solution in user['solutions']
    ] if user else []
    limit = constants.TASKS_PAGINATION_LIMIT
    offset = limit * (page - 1)

    query = {
        'sort_by': sort_by,
        'sort_order': sort_order,
        'offset': offset,
        'limit': limit,
        'solved_ids': solved_ids,
        'solved': solved
    }
    tasks_response = await request.app.tasks_client.search_tasks(**query)
    tasks = tasks_response['tasks']
    for task in tasks:
        task['solved_by_you'] = task['id'] in solved_ids

    if solved == 'yes':
        count = len(solved_ids)
    else:
        count_pesponse = await request.app.tasks_client.count()
        count = count_pesponse['count']
        if solved == 'no':
            count -= len(solved_ids)
    last_page = max((count - 1) // limit + 1, 1)

    query['page'] = page
    return {
        'user': request['user'],
        'tasks': tasks,
        'query': query,
        'page': page,
        'last_page': last_page
    }


@aiohttp_jinja2.template('proposed_archives.html')
async def proposed_archives(request: web.Request):
    sort_by = request.query.get('sort_by', 'id')
    sort_order = request.query.get('sort_order', 'asc')
    page = int(request.query.get('page', 1))
    limit = constants.TASKS_PAGINATION_LIMIT
    offset = limit * (page - 1)

    query = {
        'sort_by': sort_by,
        'sort_order': sort_order,
        'offset': offset,
        'limit': limit,
    }
    tasks_response = (
        await request.app.tasks_client.search_proposed_tasks(**query)
    )
    tasks = tasks_response['tasks']
    count_pesponse = await request.app.tasks_client.proposed_count()
    count = count_pesponse['count']

    last_page = max((count - 1) // limit + 1, 1)

    query['page'] = page
    return {
        'user': request['user'],
        'tasks': tasks,
        'query': query,
        'page': page,
        'last_page': last_page
    }


@aiohttp_jinja2.template('task.html')
async def task(request: web.Request):
    user = request['user'] or {}
    task_id = int(request.query.get('id', 1))
    task = await request.app.tasks_client.get_task(task_id)
    task['text'] = prepare_text(task['text'])
    for solution in user.get('solutions', []):
        if solution['task_id'] == task['id']:
            break
    else:
        solution = None
    count_pesponse = await request.app.tasks_client.count()
    count = count_pesponse['count']
    return {
        'user': request['user'],
        'task': task,
        'solution': solution,
        'count': count
    }


@aiohttp_jinja2.template('proposed_task.html')
async def proposed_task(request: web.Request):
    task_id = int(request.query.get('id', 1))
    tasks_response = await request.app.tasks_client.get_proposed_task(task_id)
    task = tasks_response['task']
    return {
        'user': request['user'],
        'proposed_task': task,
    }


@aiohttp_jinja2.template('propose.html')
async def propose(request: web.Request):
    user = request['user'] or {}
    proposed_task = None
    if 'proposed_task_id' in user:
        task_response = await request.app.tasks_client.get_proposed_task(
            user['proposed_task_id']
        )
        proposed_task = task_response.get('task')
    return {'user': user, 'proposed_task': proposed_task}


@aiohttp_jinja2.template('publish_yourself.html')
async def publish_yourself(request: web.Request):
    return {'user': request['user']}
