#!/usr/bin/python3.6

from aiohttp import web

from common import app
from common import constants

import tasks.constants
from tasks import handlers


class TasksApp(app.App):
    def __init__(self, loop=None):
        super().__init__(
            api_filename='./tasks/api.yaml',
            log_filename=tasks.constants.LOG_FILE,
            loop=loop
        )

        self.router.add_get(
            '/tasks{slash:/?}', handlers.get_task
        )
        self.router.add_post(
            '/tasks{slash:/?}', handlers.publish_task
        )
        self.router.add_post(
            '/tasks/search{slash:/?}', handlers.search_tasks
        )
        self.router.add_get(
            '/tasks/count{slash:/?}', handlers.count_tasks
        )
        self.router.add_post(
            '/tasks/solve{slash:/?}', handlers.solve_task
        )
        self.router.add_get(
            '/proposed_tasks{slash:/?}', handlers.get_proposed_task
        )
        self.router.add_post(
            '/proposed_tasks{slash:/?}', handlers.propose_task
        )
        self.router.add_patch(
            '/proposed_tasks{slash:/?}', handlers.update_proposed_task
        )
        self.router.add_delete(
            '/proposed_tasks{slash:/?}', handlers.delete_proposed_task
        )
        self.router.add_post(
            '/proposed_tasks/search{slash:/?}', handlers.search_proposed_tasks
        )
        self.router.add_get(
            '/proposed_tasks/count{slash:/?}', handlers.count_proposed_tasks
        )


def main():
    web.run_app(
        TasksApp(),
        port=constants.TASKS_PORT,
        access_log=None,
    )


if __name__ == '__main__':
    main()
