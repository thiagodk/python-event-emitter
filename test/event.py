
import unittest
import time
import threading
import asyncio

from concurrent.futures import Future
from typing import Dict

from event_emitter import EventEmitter

class TestEvents(unittest.TestCase):
    def check_events(self, event: EventEmitter, event_counts: Dict[str, int]):
        for event_name in event.event_names:
            count = event_counts.get(event_name)
            self.assertIsNotNone(count, "Unexpected event '{}'".format(event_name))
            self.assertEqual(event.listener_count(event_name), count,
                             "Mismatch event '{}' count. Expected {:d} but have {:d}".format(event, count, event.listener_count(event_name)))

    def test_listeners(self):
        listener_add = threading.Event()
        listener_remove = threading.Event()
        listener_done = threading.Event()
        listener_once = threading.Event()
        event_tester = EventEmitter()
        def emitter_callback():
            time.sleep(10)
            event_tester.emit("test", "Running Unit Test", test_str="Test String", test_int=10)
        def create_listener_callback(event: threading.Event):
            def listener_callback(label, *, test_str, test_int):
                self.assertEqual(label, "Running Unit Test")
                self.assertEqual(test_str, "Test String")
                self.assertEqual(test_int, 10)
                self.assertIsInstance(test_str, str)
                self.assertIsInstance(test_int, int)
                event.set()
            return listener_callback
        def new_listener_callback(event_name, listener):
            if not listener_add.is_set() and event_name == "test":
                listener_add.set()
        def remove_listener_callback(event_name, listener):
            if not listener_remove.is_set() and event_name == "test":
                listener_remove.set()
        event_tester.on("removeListener", remove_listener_callback)
        self.check_events(event_tester, {"removeListener": 1})
        event_tester.on("newListener", new_listener_callback)
        self.check_events(event_tester, {"newListener": 1, "removeListener": 1})
        event_listener_callback = create_listener_callback(listener_done)
        event_tester.on("test", event_listener_callback)
        self.check_events(event_tester, {"newListener": 1, "removeListener": 1, "test": 1})
        once_listener_callback = create_listener_callback(listener_once)
        event_tester.once("test", once_listener_callback)
        self.check_events(event_tester, {"newListener": 1, "removeListener": 1, "test": 2})
        thr = threading.Thread(target=emitter_callback)
        thr.start()
        listener_add.wait(1)
        thr.join()
        listener_once.wait(1)
        self.check_events(event_tester, {"newListener": 1, "removeListener": 1, "test": 1})
        listener_done.wait(1)
        event_tester.remove_listener("test", event_listener_callback)
        listener_remove.wait(1)
        self.check_events(event_tester, {"newListener": 1, "removeListener": 1})
        self.assertTrue(listener_done.is_set(), "Listener call failed")
        self.assertTrue(listener_once.is_set(), "Listener (once) call failed")
        self.assertTrue(listener_add.is_set(), "Listener for newListener failed")
        self.assertTrue(listener_remove.is_set(), "Listener for removeListener failed")
        self.assertEqual(len(event_tester.event_names), 2, "Mismatch event counts")

    def test_async_listeners(self):
        loop = asyncio.get_event_loop()
        future_add = Future()
        future_remove = Future()
        future_done = Future()
        future_once = Future()
        event_tester = EventEmitter()
        async def emitter_callback():
            await asyncio.sleep(10)
            event_tester.emit("test", "Running Unit Test", test_str="Test String", test_int=10)
        def create_listener_callback(future: Future):
            async def listener_callback(label, *, test_str, test_int):
                try:
                    self.assertEqual(label, "Running Unit Test")
                    self.assertEqual(test_str, "Test String")
                    self.assertEqual(test_int, 10)
                    self.assertIsInstance(test_str, str)
                    self.assertIsInstance(test_int, int)
                except BaseException as exc:
                    future.set_exception(exc)
                else:
                    future.set_result(True)
            return listener_callback
        async def new_listener_callback(event_name, listener):
            if not future_add.done() and event_name == "test":
                future_add.set_result(True)
        async def remove_listener_callback(event_name, listener):
            if not future_remove.done() and event_name == "test":
                future_remove.set_result(True)
        event_tester.on("removeListener", remove_listener_callback)
        self.check_events(event_tester, {"removeListener": 1})
        event_tester.on("newListener", new_listener_callback)
        self.check_events(event_tester, {"newListener": 1, "removeListener": 1})
        event_listener_callback = create_listener_callback(future_done)
        event_tester.on("test", event_listener_callback)
        self.check_events(event_tester, {"newListener": 1, "removeListener": 1, "test": 1})
        once_listener_callback = create_listener_callback(future_once)
        event_tester.once("test", once_listener_callback)
        self.check_events(event_tester, {"newListener": 1, "removeListener": 1, "test": 2})
        loop.run_until_complete(emitter_callback())
        loop.run_until_complete(asyncio.sleep(1)) # Workaround for pending tasks to complete
        event_tester.remove_listener("test", event_listener_callback)
        loop.run_until_complete(asyncio.sleep(1))
        self.check_events(event_tester, {"newListener": 1, "removeListener": 1})
        self.assertTrue(future_done.result(1), "Listener call failed")
        self.assertTrue(future_once.result(1), "Listener (once) call failed")
        self.assertTrue(future_add.result(1), "Listener for newListener failed")
        self.assertTrue(future_remove.result(1), "Listener for removeListener failed")
        self.assertEqual(len(event_tester.event_names), 2, "Mismatch event counts")

if __name__ == "__main__":
    unittest.main()

