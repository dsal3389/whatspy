import time
import re
import json
import asyncio

from .mixins import MessageWithResponseMixin


class MessageIdentifiers:
    """
    used for event decorators to identify a message
    by tag
    """
    TIME = ('\d*\.--\d*', re.M)
    S = ('s\d', re.M)


class MessageTags:
    """
    used by messages to send data with tag
    """
    TIME = lambda : int(time.time())


