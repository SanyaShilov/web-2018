#!/usr/bin/python3.6

import os

from aiohttp import web
import jinja2
import aiohttp_jinja2

from common import app
from common import constants

import projecteuler.constants
from projecteuler import handlers
from projecteuler import middlewares
from projecteuler import pages
from projecteuler import tasks_client
from projecteuler import users_client
from projecteuler import utils


class ProjectEulerApp(app.App):
    def __init__(self, loop=None):
        super().__init__(
            log_filename=projecteuler.constants.LOG_FILE,
            log_response_text=False,
            log_skip_urls=['/home/sanyash/bootstrap', '/projecteuler/static'],
            loop=loop
        )
        self.users_client = users_client.UsersClient(loop=loop)
        self.tasks_client = tasks_client.TasksClient(loop=loop)

        self.router.add_get(
            '/', pages.about
        )
        self.router.add_get(
            '/about{slash:/?}', pages.about
        )
        self.router.add_get(
            '/register{slash:/?}', pages.register
        )
        self.router.add_post(
            '/register{slash:/?}', handlers.register
        )
        self.router.add_get(
            '/sign_in{slash:/?}', pages.sign_in
        )
        self.router.add_post(
            '/sign_in{slash:/?}', handlers.sign_in
        )
        self.router.add_post(
            '/sign_out{slash:/?}', handlers.sign_out
        )
        self.router.add_get(
            '/account{slash:/?}', pages.account
        )
        self.router.add_post(
            '/account{slash:/?}', handlers.change_info
        )
        self.router.add_get(
            '/archives{slash:/?}', pages.archives
        )
        self.router.add_get(
            '/task{slash:/?}', pages.task
        )
        self.router.add_post(
            '/task{slash:/?}', handlers.submit_answer
        )
        self.router.add_get(
            '/statistics{slash:/?}', pages.statistics
        )
        self.router.add_get(
            '/propose{slash:/?}', pages.propose
        )
        self.router.add_post(
            '/propose{slash:/?}', handlers.propose
        )
        self.router.add_get(
            '/proposed_archives{slash:/?}', pages.proposed_archives
        )
        self.router.add_get(
            '/proposed_task{slash:/?}', pages.proposed_task
        )
        self.router.add_post(
            '/reject{slash:/?}', handlers.reject
        )
        self.router.add_post(
            '/publish{slash:/?}', handlers.publish
        )
        self.router.add_get(
            '/publish_yourself{slash:/?}', pages.publish_yourself
        )
        self.router.add_post(
            '/publish_yourself{slash:/?}', handlers.publish_yourself
        )

        aiohttp_jinja2.setup(
            self, loader=jinja2.FileSystemLoader('./projecteuler/static/html')
        )
        dirname = os.path.dirname(__file__)
        self.router.add_static(
            '/projecteuler/static/',
            os.path.join(dirname, 'static')
        )
        self.router.add_static(
            '/home/sanyash/bootstrap',
            '/home/sanyash/bootstrap'
        )

        self.middlewares.append(middlewares.authenticate)
        self.middlewares.append(middlewares.redirect)

        self.on_shutdown.append(utils.on_shutdown)

def main():
    web.run_app(
        ProjectEulerApp(),
        port=constants.PROJECTEULER_PORT,
        access_log=None,
    )


if __name__ == '__main__':
    main()
