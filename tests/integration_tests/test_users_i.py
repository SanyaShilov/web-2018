import pytest


@pytest.mark.parametrize(
    'login, password, expected_status',
    [
        ('lg', 'password', 400),
        ('login', 'pw', 400),
        ('looooooooooooooooogiiiiiiiiiiiiiiiiin', 'password', 400),
        ('login', 'paaaaaaaaassssssssswooooooooooord', 400),
        ('login!@#', 'password', 400),
        ('login', 'password!@#', 400),
        ('login0', 'password', 422),
        ('login', 'password1', 422),
        ('login', 'password', 201)
    ]
)
async def test_register(db, users_client, oid,
                        login, password, expected_status):
    count_before = await db.users.count_documents({})
    response = await users_client.post(
        '/register',
        json={
            'login': login,
            'password': password,
        }
    )
    result = await response.json()
    count_after = await db.users.count_documents({})

    assert response.status == expected_status
    if expected_status == 201:
        assert result['token'] == str(oid)
        assert count_after == count_before + 1
    else:
        assert 'reason' in result
        assert count_after == count_before


async def test_sign_out(db, users_client):
    user = await db.users.find_one({'token': '5be12c3c4b3e4d019fa99fa3'})
    assert user
    response = await users_client.post(
        '/sign_out',
        json={},
        headers={
            'projecteuler-user-token': '5be12c3c4b3e4d019fa99fa3'
        }
    )
    assert response.status == 200
    user = await db.users.find_one({'token': '5be12c3c4b3e4d019fa99fa3'})
    assert not user


@pytest.mark.parametrize(
    'login, password, expected_status, expected_token',
    [
        ('login0', 'password1', 403, None),
        ('login0', 'password0', 200, '5be1e9ea4b3e4d0db08713b7'),
        ('login1', 'password1', 200, '5be12c3c4b3e4d019fa99fa3')
    ]
)
async def test_sign_in(db, users_client, oid,
                       login, password, expected_status, expected_token):
    response = await users_client.post(
        '/sign_in',
        json={
            'login': login,
            'password': password,
        },
    )
    assert response.status == expected_status
    result = await response.json()
    assert result.get('token') == expected_token


async def test_me(users_client):
    response = await users_client.get(
        '/me',
        headers={
            'projecteuler-user-token': '5be12c3c4b3e4d019fa99fa3'
        }
    )
    assert response.status == 200
    result = await response.json()
    assert result == {
        'user': {
            'login': 'login1',
            'password': 'password1',
            'solutions': [
                {
                    'task_id': 1,
                    'submitted': '2018-11-06T12:34:56',
                }
            ],
            'country': 'Russia',
            'programming_language': 'Python',
            'solutions_count': 1,
            'proposed_task_id': 2,
            'admin': True,
        }
    }


@pytest.mark.parametrize(
    'data, expected_status',
    [
        (
            {
                'login': 'login0',
            },
            422
        ),
        (
            {
                'password': 'password0'
            },
            422
        ),
        (
            {
                'login': 'login1'
            },
            200,
        ),
        (
            {
                'password': 'password1'
            },
            200
        ),
        (
            {
                'login': 'login2',
                'password': 'password2'
            },
            200
        ),
        (
            {
                'email': 'some_email',
                'phone': 'some_phone',
                'country': 'some_country',
                'programming_language': 'some_programming_language'
            },
            200
        )
    ]
)
async def test_change_info(users_client,
                           data, expected_status):
    response = await users_client.post(
        '/change_info',
        json=data,
        headers={
            'projecteuler-user-token': '5be12c3c4b3e4d019fa99fa3'
        }
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'task_id, expected_status, expected_db_result',
    [
        (1, 422, {'solutions_count': 1}),
        (2, 200, {'solutions_count': 2})
    ]
)
async def test_solve(db, users_client,
                     task_id, expected_status, expected_db_result):
    response = await users_client.post(
        '/solve',
        json={
            'task_id': task_id
        },
        headers={
            'projecteuler-user-token': '5be12c3c4b3e4d019fa99fa3'
        }
    )
    assert response.status == expected_status
    solutions_count = await db.users.find_one(
        {
            'login': 'login1'
        },
        {
            '_id': False,
            'solutions_count': True
        }
    )
    assert solutions_count == expected_db_result


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
async def test_statistics(db, users_client,
                          detailed, detailed_statistics):
    params = {'detailed': detailed} if detailed else None
    response = await users_client.get(
        '/statistics',
        params=params,
    )
    assert response.status == 200
    result = await response.json()
    statistics = {
        'users': 2,
        'countries': 1,
        'programming_languages': 2,
        'total_solutions': 1,
        'average_solutions': 0.5,
    }
    statistics.update(detailed_statistics)
    assert result == {'statistics': statistics}
