import re
import functools
import logging

log = logging.getLogger(__name__)


class MessageEvents:
    """
    messages event called when a websocket
    recv a message, if its from type "str" it will check next to
    those events, meaning if some user send a command, the function here wont be called!
    """

    @staticmethod
    def regex(regex:tuple):
        """
        accepting regex settings
        example:
            @MessageEvent.regex(('\d*foo\d*', re.M))
            async def foo(*args, **kawrgs):
                ...
        """

        def deco(func):
            EventsManager.add_event_starts_with(
                re.compile(*regex), 
                func
            )
            log.info(
                'added %s to MessageEvent(regex)'
                %(func.__name__)
            )

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return deco
