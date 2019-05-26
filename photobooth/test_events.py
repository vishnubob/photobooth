import time
from unittest import TestCase, mock
from . events import EventManager, Event

class TestEventObject(TestCase):
    TestValue_Timestamp = 123

    @mock.patch("time.time", mock.MagicMock(return_value=TestValue_Timestamp))
    def test_constructor(self):
        name = "test"
        data = {name: "1"}
        ev = Event(name="test", data=data)
        self.assertEqual(ev.name, name)
        self.assertEqual(ev.data, data)
        self.assertEqual(ev.timestamp, self.TestValue_Timestamp)

    def test_constuctor_error(self):
        with self.assertRaises(ValueError):
            ev = Event()
        with self.assertRaises(TypeError):
            ev = Event(name=1)

class TestEventManager(TestCase):
    def setUp(self):
        man = EventManager()
        man.reset_instance()

    def test_add_handler_error(self):
        man = EventManager()
        with self.assertRaises(ValueError):
            man.add_handler(callback=str)
        with self.assertRaises(TypeError):
            man.add_handler(name=1, callback=str)
        with self.assertRaises(ValueError):
            man.add_handler(name="1")
        with self.assertRaises(TypeError):
            man.add_handler(name="1", callback=1)

    def test_add_handler_error(self):
        man = EventManager()
        with self.assertRaises(ValueError):
            man.remove_handler(callback=str)
        with self.assertRaises(TypeError):
            man.remove_handler(name=1, callback=str)
        with self.assertRaises(ValueError):
            man.remove_handler(name="1")
        with self.assertRaises(TypeError):
            man.remove_handler(name="1", callback=1)
        with self.assertRaises(KeyError):
            man.remove_handler(name="1", callback=str)

    def test_add_fire_error(self):
        man = EventManager()
        with self.assertRaises(TypeError):
            man.remove_handler(fire=1)

    def test_fire(self):
        name = "test"
        result = [False]
        data = ["data"]
        def test_handler(ev):
            self.assertEqual(ev.name, name)
            self.assertEqual(ev.data, data)
            result[0] = True
        man = EventManager()
        man.add_handler(name, test_handler)
        ev = Event(name=name, data=data)
        man.fire(ev)
        self.assertTrue(all(result))

    def test_removal(self):
        name = "test"
        result = [False]
        def test_handler(ev):
            result[0] = True
        man = EventManager()
        man.add_handler(name, test_handler)
        ev = Event(name=name)
        man.fire(ev)
        self.assertTrue(all(result))
        result[0] = False
        man.remove_handler(name, test_handler)
        man.fire(ev)
        self.assertFalse(all(result))
