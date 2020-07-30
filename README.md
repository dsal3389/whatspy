
# whatspy
the unoffical whatsapp API that uses the whatsapp websockets, 

## current state
the current lib is under build and unpublished yet

## aim
the aim of this lib is to let people make a personal "bot" 
or a notify sort of thing, aiming to be fast, efficient, simple

## Big picture
![whatspy-arch](/images/whatspy-arch.png)

### explenation
the `client` and the `websocket` only communicate 1o1 **only at the authentication (at the start)**
after that the `client` wont recv direct messages from the `websocket`, the recv messages will go to the `manager`
that will direct them to the correct path, if the message is bytes the `manager` will call `enc_manager` to dencrypt the message, after that
the message will be send to the `event manager` to check if there is any event waiting for the recved message
