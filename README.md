
# About Python Event Emitter

This is a python implementation for JavaScript-like EventEmitter class

# Usage

If you want that your class use a JavaScript-like **on()** and **emit()** approaches for event handling, just extends your class with EventEmitter class just the same as you do in JavaScript

## Example

```python

from event_emitter import EventEmitter

class MyEventClass(EventEmitter):
    def __init__(self):
        super().__init__()
        print("This is a EventEmitter example")
        self.on("my-event", lambda value: print(f"my-event got value: {value}"))

if __name__ == "__main__":
    event_example = MyEventClass()
    event_example.emit("my-event", "Test")

```

## Classes

### EventEmitter

This is your base class for your event-based class. This is the one that implements EventEmitter JavaScript-like class with *on* and *emit* methods for handling and emitting events.

### EventHandler

This is a container for events callback you can add or remove functions by using **append** and **remove** methods or **+=** and **-=*** operator. It is an iterable object, so you can iterate through it to get all callback functions. It is also a callable object, so if you want to call all functions, just call this EventHandler instance object, this is the way how EventEmitter run callback functions when an event happens

#### Example

```python

from event_emitter import EventHandler

handler = EventHandler()
handler += lambda label: print(f"First callback of f{label}")
handler += lambda label: print(f"Second callback of f{label}")
handler += lambda label: print(f"Third callback of f{label}")
handler("test")

```

### EventCallable

This is a wrapper for event callback. This class implements an *once* static method decorator for handling once-call event handler, you can pass an asyncio event loop object to *loop* parameter in case of using an async function and you want to execute it on a event loop different from your current event loop.

#### Example

```python

from event_emitter import EventCallable, EventEmitter

event_example = EventEmitter()

@EventCallable.once(event_example, "test")
def callback(label):
    print(f"Event called with label: {label}")

event_example.on("test", callback)

event_example.emit("test", "First call")
event_example.emit("test", "Second call")

```

# Internals

## Event Handling

All events of **EventEmitter** class is execute on a separate thread to avoid event processing to block your application main thread. If your event handler is a coroutine then it is executed on your current event loop. If you want to use a different event loop, then you must use a **EventCallable** class for your event callback and pass a different event loop object to it's argument
