"""
    message aliases will be stored here

    instead of creating object that be flexible and compute the required message
    the functions will return the message as "python" and the websocket will
    convert it to sendable stream (bytes/string)
"""

import json, time
from .message import MessageIdentifiers, MessageTags


def init_message(client_id):
    """
    sended to let whatsapp know the connection type
    to list it on your phone
    """
    payload = [
        'admin',
        'init',
        [2, 2029, 4],
        ['Windows', 'Chrome', '10'],
        client_id,
        True
    ]
    return (MessageTags.TIME, payload)

def reref():
    """
    sended to request a new QR code
    """
    payload = [
        'admin', 
        'Conn',
        'reref'
    ]
    return (MessageTags.TIME, payload)
    
def restore_session(token, server_token, client_id):
    payload = [
        'admin',
        'login',
        str(token, 'utf-8'),
        str(server_token, 'utf-8'),
        client_id,
        'takeover'
    ]
    return (MessageTags.TIME, payload)

def disconnect_session():
    payload = [
        'admin',
        'Conn',
        'disconnect'
    ]
    tag = lambda : 'goodbye,'
    return (tag, payload)

def alive():
    return (int(time.time()), )
