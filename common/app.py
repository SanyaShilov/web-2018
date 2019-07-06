#!/usr/lib/python3.6

from aiohttp import web

from common import db
from common import logs
from common import swagger2_validator
from common import utils


class App(web.Application):
    def __init__(self, api_filename=None, log_filename=None,
                 log_response_text=True, log_skip_urls=None, loop=None):
        super().__init__(loop=loop)

        if log_filename:
            logs.configure_log(log_filename)
            self.middlewares.append(
                logs.log_middleware(
                    log_response_text=log_response_text,
                    log_skip_urls=log_skip_urls,
                )
            )

        self.middlewares.append(utils.raise_http_exception)

        if api_filename:
            self.swagger2_validator = swagger2_validator.Swagger2Validator(
                api_filename
            )
            self.middlewares.append(
                swagger2_validator.swagger2_validation_middleware
            )

        self.db = db.Database()
