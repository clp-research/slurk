# How to: Bots

## Basic introduction:

Bots use **commands** for communication. They react on either **client commands** (e.g. if a user types in /say_hello or /say_hello) or **events** (e.g. a new message in the chat room), and respond by sending commands to the server. All input and output commands have to be specified within the bot file.

* Some events are described [**here**](https://bitbucket.org/dsgbielefeld/server/wiki/Events)

* Client commands have to be defined within the bot file.

* Some output commands are described [**here**](https://bitbucket.org/dsgbielefeld/server/wiki/Commands)

---

## Input

### Events

Events are defined in the server files, e.g. in app/main/events.py. An overview can be found [**here**](https://bitbucket.org/dsgbielefeld/server/wiki/Events).

For the bot to react to events you have to add methods to the ChatNamespace class, according to the following structure:
```
class ChatNamespace(BaseNamespace):

    def on_event(self, data):
        # do something
```
* Example: Printing room messages to the console

```
def on_message(self, data):
    print ("New room message: ", data["msg"])
```


search for *"emit('status'"* in the project folder>


### Client commands

Setting up the bot for client commands works in a similar way to server side events.

First, you have to set up a **listener** - i.e., a small piece of code to tell the server to wait for a specific command and emit an event once it occurs. Then you can add methods to the ChatNamespace class the same way as for server side events.

Listener registration uses commands within the chat namespace:

* Example: Listener registration for the client command "/say_hello":
    
    ```
    chat_namespace.emit('command', ['listen_to', 'say_hello'])
    ```

Since listeners have to be registered for specific rooms, the placement of the command within the bot file depends on whether the bot can perform room changes or not.

* Static bots which are unable to switch rooms (shortened example from minimal bot):

    ```
    class LoginNamespace(BaseNamespace):
        def on_login_status(self, data):
            global chat_namespace
            if data["success"]:
                chat_namespace = socketIO.define(ChatNamespace, '/chat')
    
                # register to commands
                chat_namespace.emit('command', ['listen_to', 'say_hello'])
    ```

* Bots which are able to perform room changes (shortened example from multi_bot):

    ```
    class ChatNamespace(BaseNamespace):
    
        def on_new_task_room(self, data):
            if data['task']['name'] != 'meetup':
                return
    
            room = data['room']
            self.emit('join_task', {'room': room['id']})
    
            # register to commands
            self.emit("command", {'room': room['id'], 'data': ['listen_to', 'say_hello']})
    ```

Once a listener is registered successfully, a corresponding method can be added to the ChatNamespace class:

```
class ChatNamespace(BaseNamespace):

    def on_say_hello(self, data):
        # do something
```

---

## Output

Output commands are devided in two namespaces: Login and chat. Parameters have to be passed as dictionaries in both cases. [**Here**](https://bitbucket.org/dsgbielefeld/server/wiki/Commands) you can find examples for output server commands.

Commands within the **login namespace** are used for connecting the bot to a room:

* connect_with_token:

    ```
    login_namespace.emit('connectWithToken', {'token': args.token, 'name': "BotName"})
    ```

Commands within the **chat namespace** are used to perform various tasks once the bot is connected to a room. Examples:

* sending a message:

    ```
    chat_namespace.emit("text", {"msg": "Hello World!", "room":data['room']['id']})
    ```
* disconnecting from a room:

    ```
    chat_namespace.emit("disconnect")
    ```

Output commands are usually called within methods of the ChatNamespace class:

```
class ChatNamespace(BaseNamespace):

    def on_say_hello(self, data):
        self.emit("text", {"msg": "Hello!", "room":data['room']['id']}
        )
```

---
