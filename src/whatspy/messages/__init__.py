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
        ['Bot', '', '1.0'],
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
        token,
        server_token,
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
    return ('goodbye,', payload)

def challenge_response(challenge, server_token, client_id):
    payload = [
        'admin',
        'challenge',
        challenge, 
        server_token,
        client_id
    ]
    return (MessageTags.TIME, payload)

def remember_me(state):
    payload = [
        'admin',
        'remember',
        state
    ]
    return (MessageTags.TIME, payload)
