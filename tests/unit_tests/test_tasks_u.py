import datetime

import pytest

from tasks import _tasks


@pytest.mark.parametrize(
    'task_id, expected_result',
    [
        (
            1,
            {
                'status': 'ok',
                'task': {
                    '_id': 1,
                    'answer': 1,
                    'difficulty': 25,
                    'published': datetime.datetime(2018, 10, 6, 12, 34, 56),
                    'solved_by': 1,
                    'text': 'text1',
                    'title': 'title1'
                }
            }
        ),
        (
            3,
            {'reason': 'not_found', 'status': 'error'}
        )
    ]
)
async def test_get_task(db, task_id, expected_result):
    result = await _tasks.get_task(db, task_id)
    assert result == expected_result


async def test_publish_task(db):
    result = await _tasks.publish_task(
        db, 'new_title', 'new_text', 'new_answer', 50
    )
    assert result == {'status': 'ok'}
    task = await db.tasks.find_one({'_id': 3})
    assert task == {
        '_id': 3,
        'title': 'new_title',
        'text': 'new_text',
        'answer': 'new_answer',
        'difficulty': 50,
        'solved_by': 0,
        'published': datetime.datetime(2018, 11, 14, 23, 9, 1)
    }


async def test_propose_task(db):
    result = await _tasks.propose_task(
        db, 'new_title', 'new_text', 'new_answer', 50
    )
    assert result == {'status': 'ok', 'task_id': 3}
    task = await db.proposed_tasks.find_one({'_id': 3})
    assert task == {
        '_id': 3,
        'title': 'new_title',
        'text': 'new_text',
        'answer': 'new_answer',
        'difficulty': 50,
        'proposed': datetime.datetime(2018, 11, 14, 23, 9, 1)
    }


@pytest.mark.parametrize(
    'task_id, expected_result, expected_db_result',
    [
        (
            1,
            {'status': 'ok'},
            {
                '_id': 1,
                'solved_by': 2,
            }
        ),
        (
            3,
            {'status': 'error', 'reason': 'not_found'},
            None
        )
    ]
)
async def test_solve(db, task_id, expected_result, expected_db_result):
    result = await _tasks.solve(db, task_id)
    assert result == expected_result
    task = await db.tasks.find_one({'_id': task_id}, {'solved_by': True})
    assert task == expected_db_result


@pytest.mark.parametrize(
    'sort_by, sort_order, offset, limit, task_ids',
    [
        ('id', 'asc', 0, 0, [1, 2]),
        ('id', 'desc', 0, 0, [2, 1]),
        ('solved_by', 'asc', 0, 0, [2, 1]),
        ('id', 'asc', 1, 0, [2]),
        ('id', 'asc', 0, 1, [1]),
    ]
)
async def test_search(db, sort_by, sort_order, offset, limit, task_ids):
    result = await _tasks.search_tasks(db, sort_by, sort_order, offset, limit)
    assert result['status'] == 'ok'
    assert [task['_id'] for task in result['tasks']] == task_ids


@pytest.mark.parametrize(
    'task_id, data, expected_result, expected_db_result',
    [
        (
            1,
            {
                'title': 'new_title',
                'text': 'new_text',
                'answer': 'new_answer',
                'difficulty': 30,
            },
            {'status': 'ok'},
            {
                '_id': 1,
                'title': 'new_title',
                'text': 'new_text',
                'answer': 'new_answer',
                'difficulty': 30,
                'proposed': datetime.datetime(2018, 10, 6, 12, 34, 56),
            },
        ),
        (
            3,
            {
                'title': 'new_title',
            },
            {'status': 'error', 'reason': 'not_found'},
            None
        )
    ]
)
async def test_update_proposed_task(db, task_id, data, expected_result,
                                    expected_db_result):
    result = await _tasks.update_proposed_task(db, task_id, **data)
    assert result == expected_result
    task = await db.proposed_tasks.find_one({'_id': task_id})
    assert task == expected_db_result
