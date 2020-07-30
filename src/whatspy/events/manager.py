import asyncio
import re


def is_valid_callback(callback:callable, raise_error=False):
    valid = not asyncio.iscoroutinefunction(callback)
    if not valid and raise_error:
        raise ValueError('function %s is not coroutine' %callback.__name__)
    return valid


class EventsManager:
    _messages_regex_events = {}

    @classmethod
    def add_event_message_regex(cls, text:str, callback:callable):
        is_valid_callback(callback, raise_error=True)
        if text in cls._messages_regex_events.keys():
            raise NameError('conflict, two events (message_starts_with) take the same text (%s)' %test)
        cls._messages_regex_events[text] = callback

    @classmethod
    async def get_event_message_regex(cls, text:str):
        for event_re, callback in cls._messages_regex_events.items():
            if event_re.match(text):
                yield callback

