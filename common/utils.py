import pytz

import dateutil.parser
import aiohttp
from aiohttp import web


@web.middleware
async def raise_http_exception(request, handler):
    if request.match_info.http_exception is not None:
        raise request.match_info.http_exception
    return await handler(request)


def parse_timestring(time_string, timezone='UTC'):
    """Parse timestring into naive UTC

    :param time_string: in ISO-8601 format
    :param timezone: if time_string contains no timezone, this argument is used
    :return: naive time in UTC
    """
    time = dateutil.parser.parse(time_string)
    if time.tzinfo is None:
        time = pytz.timezone(timezone).localize(time)
    utctime = time.astimezone(pytz.utc).replace(tzinfo=None)

    return utctime


async def create_session(loop=None):
    return aiohttp.ClientSession(loop=loop)


def startswith_one(url, prefixes):
    return any(str(url).startswith(prefix) for prefix in prefixes)
