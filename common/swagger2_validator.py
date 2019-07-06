import flex
from aiohttp import web


class Swagger2Validator:
    def __init__(self, yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as yaml_file:
            self._schema = flex.core.load_source(yaml_file)

    async def validate_request(self, request):
        raw_request = await self._raw_request(request)
        flex.core.validate_api_request(
            schema=self._schema,
            raw_request=raw_request,
        )
        return raw_request

    async def validate_response(self, raw_request, response):
        try:
            content = response.text
        except AttributeError:
            content = None

        raw_response = flex.http.Response(
            request=raw_request,
            url=raw_request.url,
            content=content,
            status_code=response.status,
            content_type=response.content_type,
            headers=response.headers,
        )

        flex.core.validate_api_response(
            schema=self._schema,
            raw_response=raw_response,
            request_method=raw_request.method.lower()
        )

    @staticmethod
    async def _raw_request(request):
        request_body = await request.text()
        return flex.http.Request(
            method=request.method.lower(),
            url=str(request.url),
            content_type=request.content_type if request_body != '' else None,
            headers=request.headers,
            body=request_body,
        )


@web.middleware
async def swagger2_validation_middleware(request, handler):
    try:
        raw_request = (
            await request.app.swagger2_validator.validate_request(request)
        )
    except ValueError as exc:
        return web.json_response(
            {
                'reason': str(exc)
            },
            status=web.HTTPBadRequest.status_code
        )
    response = await handler(request)
    try:
        await request.app.swagger2_validator.validate_response(
            raw_request, response,
        )
    except ValueError as exc:
        return web.json_response(
            {
                'reason': str(exc)
            },
            status=web.HTTPInternalServerError.status_code
        )
    return response
