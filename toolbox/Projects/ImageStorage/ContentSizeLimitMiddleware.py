# Modified from https://github.com/steinnes/content-size-limit-asgi
from fastapi import HTTPException, status


class ContentSizeLimitMiddleware:
    """Content size limiting middleware for ASGI applications.
    """

    def __init__(self, app: any, max_content_size: int):
        """
        Args:
            app (any): ASGI application.
            max_content_size (int): The maximum content size allowed in bytes.
        """
        self.app = app
        self.max_content_size = max_content_size

    def receive_wrapper(self, receive):
        received = 0

        async def inner():
            nonlocal received
            message = await receive()
            if message["type"] != "http.request" \
                    or self.max_content_size is None:
                return message
            body_len = len(message.get("body", b""))
            received += body_len
            if received > self.max_content_size:
                raise HTTPException(
                    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    f"Maximum content size limit ({self.max_content_size})"
                    f" exceeded ({received} bytes read)"
                )
            return message
        return inner

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        wrapper = self.receive_wrapper(receive)
        await self.app(scope, wrapper, send)
