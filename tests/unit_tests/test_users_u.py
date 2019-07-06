import datetime

import pytest

from users import _users


@pytest.mark.parametrize(
    'login, password, expected_result, expected_count',
    [
        (
            'login0',
            'password',
            {'status': 'error', 'reason': 'login_exists'},
            2
        ),
        (
            'login',
            'password1',
            {'status': 'error', 'reason': 'password_exists'},
            2
        ),
        (
            'login',
            'password',
            {'status': 'ok', 'token': '5be1e9ea4b3e4d0db08713b7'},
            3
        )
    ]
)
async def test_register(db, oid,
                        login, password, expected_result, expected_count):
    result = await _users.register(db, login, password)
    assert result == expected_result
    users_count = await db.users.count_documents({})
    assert users_count == expected_count


async def test_sign_out(db):
    user = await db.users.find_one({'token': '5be12c3c4b3e4d019fa99fa3'})
    assert user
    result = await _users.sign_out(db, user)
    assert result == {'status': 'ok'}
    user = await db.users.find_one({'token': '5be12c3c4b3e4d019fa99fa3'})
    assert not user


@pytest.mark.parametrize(
    'login, password, expected_result',
    [
        (
            'wrong_login',
            'password',
            {'status': 'error', 'reason': 'wrong_login'}
        ),
        (
            'login0',
            'password1',
            {'status': 'error', 'reason': 'wrong_password'},
        ),
        (
            'login0',
            'password0',
            {'status': 'ok', 'token': '5be1e9ea4b3e4d0db08713b7'}
        ),
        (
            'login1',
            'password1',
            {'status': 'ok', 'token': '5be12c3c4b3e4d019fa99fa3'}
        )
    ]
)
async def test_sign_in(db, oid,
                       login, password, expected_result):
    result = await _users.sign_in(db, login, password)
    assert result == expected_result


@pytest.mark.parametrize(
    'data, expected_result',
    [
        (
            {
                'login': 'login0',
            },
            {'status': 'error', 'reason': 'login_exists'}
        ),
        (
            {
                'password': 'password0'
            },
            {'status': 'error', 'reason': 'password_exists'}
        ),
        (
            {
                'login': 'login1'
            },
            {'status': 'ok'}
        ),
        (
            {
                'password': 'password1'
            },
            {'status': 'ok'}
        ),
        (
            {
                'login': 'login2',
                'password': 'password2'
            },
            {'status': 'ok'}
        ),
        (
            {
                'email': 'some_email',
                'phone': 'some_phone',
                'country': 'some_country',
                'programming_language': 'some_programming_language'
            },
            {'status': 'ok'}
        )
    ]
)
async def test_change_info(db,
                           data, expected_result):
    user = await db.users.find_one({'token': '5be12c3c4b3e4d019fa99fa3'})
    result = await _users.change_info(db, user, **data)
    assert result == expected_result


@pytest.mark.parametrize(
    'task_id, expected_result, expected_db_result',
    [
        (
            1,
            {'status': 'error', 'reason': 'task_id_exists'},
            {
                'solutions_count': 1,
                'solutions': [
                    {
                        "task_id": 1,
                        "submitted": datetime.datetime(2018, 11, 6, 12, 34, 56)
                    }
                ]
            }
        ),
        (
            2,
            {'status': 'ok'},
            {
                'solutions_count': 2,
                'solutions': [
                    {
                        "task_id": 1,
                        "submitted": datetime.datetime(2018, 11, 6, 12, 34, 56)
                    },
                    {
                        "task_id": 2,
                        "submitted": datetime.datetime(2018, 11, 14, 23, 9, 1)
                    }
                ]
            }
        )
    ]
)
async def test_solve(db,
                     task_id, expected_result, expected_db_result):
    user = await db.users.find_one({'token': '5be12c3c4b3e4d019fa99fa3'})
    result = await _users.solve(db, user, task_id)
    assert result == expected_result
    db_result = await db.users.find_one(
        {'token': '5be12c3c4b3e4d019fa99fa3'},
        {
            '_id': False,
            'solutions': True,
            'solutions_count': True,
        }
    )
    assert db_result == expected_db_result


async def test_mark_propose(db):
    user = await db.users.find_one({'token': '5be12c3c4b3e4d019fa99fa3'})
    await _users.mark_propose(db, user, 3)
    user = await db.users.find_one({'token': '5be12c3c4b3e4d019fa99fa3'})
    assert user['proposed_task_id'] == 3


async def test_unmark_propose(db):
    await _users.unmark_propose(db, 2)
    user = await db.users.find_one({'token': '5be12c3c4b3e4d019fa99fa3'})
    assert 'proposed_task_id' not in user


@pytest.mark.parametrize(
    'detailed, detailed_statistics',
    [
        (
            None,
            {}
        ),
        (
            'countries',
            {
                'detailed_countries': [
                    {
                        'country': 'Russia',
                        'users': 1,
                        'average_solutions': 1
                    }
                ]
            }
        ),
        (
            'programming_languages',
            {
                'detailed_programming_languages': [
                    {
                        'programming_language': 'C++',
                        'users': 1,
                        'average_solutions': 0
                    },
                    {
                        'programming_language': 'Python',
                        'users': 1,
                        'average_solutions': 1
                    },
                ]
            }
        ),
        (
            'solutions',
            {
                'detailed_solutions': [
                    {
                        'number_of_tasks': 0,
                        'users_solved_exactly': 1,
                        'users_solved_at_least': 2,
                    },
                    {
                        'number_of_tasks': 1,
                        'users_solved_exactly': 1,
                        'users_solved_at_least': 1,
                    },
                ]
            }
        )
    ]
)
async def test_statistics(db, detailed, detailed_statistics):
    result = await _users.statistics(db, detailed)
    statistics = {
        'users': 2,
        'countries': 1,
        'programming_languages': 2,
        'total_solutions': 1,
        'average_solutions': 0.5,
    }
    statistics.update(detailed_statistics)
    assert result == statistics
