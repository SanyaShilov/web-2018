import logging

from aiohttp import web

from common import utils


LOG_FORMAT = (
    'timestamp=%(asctime)s\n'
    'level=%(levelname)s\n'
    'text=%(message)s\n'
)


def configure_log(filename):
    logging.basicConfig(
        filename=filename,
        filemode='w',
        format=LOG_FORMAT,
        level=logging.DEBUG
    )


def log_middleware(log_response_text=True, log_skip_urls=None):
    log_skip_urls = log_skip_urls or []

    @web.middleware
    async def _log_middleware(request, handler):
        if utils.startswith_one(request.rel_url, log_skip_urls):
            return await handler(request)

        request.app.logger.info(
            'Request %s to %s came with text %s',
            request.method,
            request.rel_url,
            (await request.text()),
        )
        response = await handler(request)
        log_args = (
            'Request %s to %s finished with code %s and text %s',
            request.method,
            request.rel_url,
            response.status,
            response.text if log_response_text else '...'
        )
        if response.status < 400:
            request.app.logger.info(*log_args)
        elif 400 <= response.status < 500:
            request.app.logger.warning(*log_args)
        else:
            request.app.logger.error(*log_args)
        return response

    return _log_middleware
