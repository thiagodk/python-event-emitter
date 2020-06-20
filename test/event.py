
import unittest
import time
import threading
import asyncio

from concurrent.futures import Future

from event_emitter import EventEmitter

class TestEvents(unittest.TestCase):
    def test_listeners(self):
        listener_done = threading.Event()
        event_tester = EventEmitter()
        def emitter_callback():
            time.sleep(10)
            event_tester.emit("test", "Running Unit Test", test_str="Test String", test_int=10)
        def listener_callback(label, *, test_str, test_int):
            self.assertEqual(label, "Running Unit Test")
            self.assertEqual(test_str, "Test String")
            self.assertEqual(test_int, 10)
            self.assertIsInstance(test_str, str)
            self.assertIsInstance(test_int, int)
            listener_done.set()
        event_tester.on("test", listener_callback)
        thr = threading.Thread(target=emitter_callback)
        thr.start()
        thr.join()
        listener_done.wait(1)
        self.assertTrue(listener_done.is_set())

    def async_test_listeners(self):
        future = Future()
        loop = asyncio.get_event_loop()
        event_tester = EventEmitter()
        async def emitter_callback():
            await asyncio.sleep(10)
            event_tester.emit("test", "Running Unit Test", test_str="Test String", test_int=10)
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
        event_tester.on("test", listener_callback)
        loop.run_until_complete(emitter_callback())
        self.assertTrue(future.result(1))

if __name__ == "__main__":
    unittest.main()

