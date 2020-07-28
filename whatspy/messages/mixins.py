import asyncio


class MessageWithResponseMixin:
    """
    making the massage expect a response
    this used only to send data from the client to the websocket
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop = asyncio.get_event_loop()
        self.response = self._loop.create_future()

        callback = kwargs.pop('callback', None)
        if callback is not None and callable(callback):
            self.response.add_done_callback(callback)

    def _set_response(self, response):
        self.response.set_result(response)

    def __await__(self):
        return self.response.__await__()