import pytest


@pytest.mark.parametrize(
    'data, expected_ids',
    [
        (
            {},
            [1, 2],
        ),
        (
            {'sort_by': 'solved_by'},
            [2, 1],
        ),
        (
            {'sort_order': 'desc'},
            [2, 1],
        ),
        (
            {'offset': 1},
            [2],
        ),
        (
            {'limit': 1},
            [1],
        ),
        (
            {'solved_ids': [1], 'solved': 'yes'},
            [1],
        ),
        (
            {'solved_ids': [1], 'solved': 'no'},
            [2],
        ),
    ]
)
async def test_search(db, tasks_client, data, expected_ids):
    response = await tasks_client.post(
        '/tasks/search',
        json=data
    )
    assert response.status == 200
    result = await response.json()
    task_ids = [task['id'] for task in result['tasks']]
    assert task_ids == expected_ids


async def test_count(tasks_client):
    response = await tasks_client.get(
        '/tasks/count'
    )
    assert response.status == 200
    result = await response.json()
    assert result == {'count': 2}


async def test_propose_task(tasks_client):
    response = await tasks_client.post(
        '/proposed_tasks',
        json={
            'title': 'new_title',
            'text': 'new_text',
            'answer': 'new_answer',
            'difficulty': 50,
        }
    )
    assert response.status == 201
    result = await response.json()
    assert result == {'id': 3}
