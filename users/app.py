#!/usr/bin/python3.6

from aiohttp import web

from common import app
from common import constants

import users.constants
from users import handlers


class UsersApp(app.App):
    def __init__(self, loop=None):
        super().__init__(
            api_filename='./users/api.yaml',
            log_filename=users.constants.LOG_FILE,
            loop=loop
        )

        self.router.add_get(
            '/me{slash:/?}', handlers.me
        )
        self.router.add_post(
            '/change_info{slash:/?}', handlers.change_info
        )
        self.router.add_post(
            '/register{slash:/?}', handlers.register
        )
        self.router.add_post(
            '/sign_in{slash:/?}', handlers.sign_in
        )
        self.router.add_post(
            '/sign_out{slash:/?}', handlers.sign_out
        )
        self.router.add_post(
            '/solve{slash:/?}', handlers.solve
        )
        self.router.add_get(
            '/statistics{slash:/?}', handlers.statistics
        )
        self.router.add_post(
            '/propose{slash:/?}', handlers.mark_propose
        )
        self.router.add_delete(
            '/propose{slash:/?}', handlers.unmark_propose
        )


def main():
    web.run_app(
        UsersApp(),
        port=constants.USERS_PORT,
        access_log=None,
    )


if __name__ == '__main__':
    main()
