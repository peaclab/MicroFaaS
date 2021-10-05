import unittest
from threading import Timer

import util


class TestIOEvent(unittest.TestCase):
    EVENT_ID = 10
    EVENT_VALUE = 9

    def setUp(self):
        self.ev = util.IOEvent(id=self.EVENT_ID)

    def tearDown(self):
        self.ev = None

    def do_set(self):
        """Timer target"""
        self.ev.set(self.EVENT_VALUE)

    def do_set_novalue(self):
        """Timer target"""
        self.ev.set()

    def test_initial_state(self):
        self.assertEqual(self.ev.id, self.EVENT_ID)
        self.assertFalse(self.ev.is_set())
        self.assertIsNone(self.ev.value)

    def test_set(self):
        self.ev.set(self.EVENT_VALUE)
        self.assertEqual(self.ev.value, self.EVENT_VALUE)
        self.assertTrue(self.ev.is_set())

    def test_clear(self):
        self.ev.set(self.EVENT_VALUE)
        self.assertIsNotNone(self.ev.value)
        self.assertTrue(self.ev.is_set())

        self.ev.clear()
        self.assertIsNone(self.ev.value)
        self.assertFalse(self.ev.is_set())

    def test_wait(self):
        t1 = Timer(2, self.do_set)
        t1.start()
        retval = self.ev.wait(timeout=4)
        self.assertEqual(retval, self.EVENT_VALUE)
        self.assertTrue(self.ev.is_set())

    def test_wait_novalue(self):
        t1 = Timer(2, self.do_set_novalue)
        t1.start()
        retval = self.ev.wait(timeout=4)
        self.assertTrue(retval)
        self.assertTrue(self.ev.is_set())

    def test_wait_timeout(self):
        with self.assertRaises(TimeoutError):
            self.ev.wait(timeout=1)
        self.assertIsNone(self.ev.value)
        self.assertFalse(self.ev.is_set())

    def test_wait_then_clear(self):
        t1 = Timer(2, self.do_set)
        t1.start()
        retval = self.ev.wait_then_clear(timeout=4)
        self.assertEqual(retval, self.EVENT_VALUE)
        self.assertIsNone(self.ev.value)
        self.assertFalse(self.ev.is_set())




