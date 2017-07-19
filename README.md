# Random Web Sockets Chat

The RandomChat application uses a Websocket API in order to carry out its functionality. By doing so, multiple clients of different implementations (such native or hybrid mobile apps) may use the same interface.

WS is a protocol that allows full-duplex communication between client and server.

The application implements its own fully websocket-based protocol, establishing two kinds of messages: server to client, and client to server messages.

This project has been developed as a coursework in the Web Architecture course.


## Operations

This section gives an specification per each of the operations that may be performed by using the Websocket API.

In WS there is no such thing as HTTP methods. Instead of it, we use a JSON representation where the operation is specified in its “type” property.


### Global Objects
The application’s protocol uses several pre-defined objects which are re-used in several of its operations, in order to be consistent and make its usage easier. Those are:

#### User
An object which represent an user. His phone is unique.

```json
{
    "name": "<the user name>", 
    "phone": "<the user phone>",
    "disconnection_date": "<last disconnection date>"
}
```

#### Brief Message
A brief representation of a message. It does not include the chat where it was sent.

```json
{
    "from": User, 
    "date": "<the date and time>", 
    "message": "<the message>"
}
```

#### Chat
An object which represents a chat room.

```json
{
    "name": "<the chat name>", 
    "members": [User],
    "owner": User
}
```

#### ChatState
An object which contains those messages that were sent while the user did not have an open connection.

```json
{
    "chat": Chat,
    "messages": [BriefMessage]
}
```

### Client to Server Operations

#### Register
A new user becomes himself known in the system. His name and phone are specified in the “user” property of the JSON representation.

This operation may be performed to register a new user, and also to login.

When the server receives this message, it will automatically send an state message to the connected device.

```json
{
    "type": "register", 
    "user": User
}
```

#### Create Chat
An user creates a new chat. 

```json
{
    "type": "create_chat", 
    "name": "<the chat name>"
}
```

#### Send Message
An user sends a message into a chat room.

The server will send a message message to all (including the sender user) the members of the chat room.

If any of the chat room’s members has not an open connection, then it is not immediately sent;  the user will receive it when he logs in again in a messages_list message.

```json
{
    "type": "send_message", 
    "chat": "<the chat name>", 
    "message": "<the message>"
}
```

#### Delete Chat
The owner of a given chat deletes it. All the members of the chat, including the new one, will receive a chat_deleted notification.

```json
{
    "type": "delete_chat", 
    "chat": "<the chat name>"
}
```

#### Add Member
A chat member adds a new member to the chat. All the members of the chat, including the new one, will receive a new_member notification.

```json
{
    "type": "add_member", 
    "chat": "<the chat name>", 
    "phone": "<the user phone>"
}
```

#### Remove Member
The chat owner removes a member form a chat room. All the members of the room will receive a member_removed notification.

```json
{
    "type": "remove_member", 
    "chat": "<the chat name>", 
    "phone": "<the user phone>"
}
```


### Server to Client Messages

#### Message
A message produced by a chat member in a chat where the user participates.

```json
{
    "type": "message",
    "chat": Chat, 
    "from": User, 
    "date": "<the date and time>", 
    "message": "<the message>"
}
```

#### State
The server sends all the chats where the user participates, and the messages that were sent while the user did not have an open connection.

```json
{
    "type": "state",
    "chats": [
        ChatState
    ]
}
```

#### New Member
A new member joined into a chat.

```json
{
    "type": "new_member",
    "chat": Chat,
    "user": User
}
```

#### Chat Deleted
A chat has been deleted.

```json
{
    "type": "chat_deleted",
    "chat": Chat
}
```

#### Member Removed
A member has been removed from a chat.

```json
{
    "type": "member_removed",
    "chat": Chat,
    "user": User
}
```



## Installation Instructions

```
pip install virtualenv
virtualenv env
./env/bin/pip install -r requirements.txt
```


## Run the Server

```
cd src/
./../env/bin/python app.py
```