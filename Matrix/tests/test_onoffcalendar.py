import unittest
import datetime
from Matrix.driver.power import OnOffCalendar

class TestOnOffCalendar(unittest.TestCase):

    def test_create_default_calendar(self):
        
        calendar = OnOffCalendar()
        self.assertIsNotNone(calendar)
        self.assertEqual(len(calendar.schedule.keys()), 7)
    
    def test_create_calendar(self):
        
        calendar_template = {
            "Monday": ("8:00", "22:00"),
            "Tuesday": ("7:00", "23:00"),
            "Wednesday": ("8:00", "00:00"),
            "Friday": ("8:00", "01:00"),
            "Saturday": ("9:00", "02:00"),
            "Sunday": ("10:00", "23:00"),
        }
        
        calendar = OnOffCalendar(calendar_template)
        self.assertIsNotNone(calendar)
        self.assertEqual(len(calendar.schedule.keys()), 7)
        self.assertEqual(calendar.schedule["Thursday"] ,  ("8:00", "22:00"))
        
    def test_expected_state(self):
        calendar_template = {
            "Monday": ("8:00", "22:00"),
            "Tuesday": ("7:00", "23:00"),
            "Wednesday": ("8:00", "00:00"),
        }
        
        calendar = OnOffCalendar(calendar_template)
        
        now:datetime.datetime = datetime.datetime(2023, 12, 18, 14, 0, 0)
        self.assertEqual(0, now.weekday())
        self.assertTrue(calendar.expected_state(now))
    
        # 8 => ON
        now = now.replace(hour=8)
        self.assertTrue(calendar.expected_state(now))
        
        # 7 => OFF
        now = now.replace(hour=7)
        self.assertFalse(calendar.expected_state(now))
        
        # 22 => ON
        now = now.replace(hour=22)
        self.assertTrue(calendar.expected_state(now))
        
        # 22:01 => Off
        now = now.replace(minute=2)
        self.assertFalse(calendar.expected_state(now))
        
        now:datetime.datetime = datetime.datetime(2023, 12, 19, 14, 0, 0)
        self.assertEqual(1, now.weekday())
        self.assertTrue(calendar.expected_state(now))
    
        # 8 => ON
        now = now.replace(hour=8)
        self.assertTrue(calendar.expected_state(now))
        
        # 7 => ON
        now = now.replace(hour=7)
        self.assertTrue(calendar.expected_state(now))
        
        # 6 => OFF
        now = now.replace(hour=6)
        self.assertFalse(calendar.expected_state(now))
        
        # 22 => ON
        now = now.replace(hour=22)
        self.assertTrue(calendar.expected_state(now))
        
        # 22:01 => ON
        now = now.replace(minute=2)
        self.assertTrue(calendar.expected_state(now))
        
        # 23:00 => ON
        now = now.replace(hour=23, minute=0)
        self.assertTrue(calendar.expected_state(now))
        
        # 23:01 => OFF
        now = now.replace(hour=23, minute=1)
        self.assertFalse(calendar.expected_state(now))
        
    def test_expected_state_with_overlap(self):
        calendar_template = {
            "Monday": ("8:00", "22:00"),
            "Tuesday": ("7:00", "23:00"),
            "Wednesday": ("8:00", "00:00"),
            "Friday": ("8:00", "01:00"),
            "Saturday": ("9:00", "02:00"),
            "Sunday": ("10:00", "23:00"),
        }
        
        calendar = OnOffCalendar(calendar_template)
        
        # test on Friday
        now:datetime.datetime = datetime.datetime(2023, 12, 22, 14, 0, 0)
        self.assertEqual(4, now.weekday())
        self.assertTrue(calendar.expected_state(now))
    
        # 8 => ON
        now = now.replace(hour=8)
        self.assertTrue(calendar.expected_state(now))
        
        # 7 => OFF
        now = now.replace(hour=7)
        self.assertFalse(calendar.expected_state(now))
        
        # 22 => ON
        now = now.replace(hour=22)
        self.assertTrue(calendar.expected_state(now))
        
        # 23:59 => ON
        now = now.replace(hour=23, minute=59)
        self.assertTrue(calendar.expected_state(now))
        
        # 00:00 => ON
        now = now.replace(hour=0, minute=0)
        self.assertTrue(calendar.expected_state(now))
        
        # Friday Night => Saturday Morning
        now:datetime.datetime = datetime.datetime(2023, 12, 23, 0, 1, 0)
        self.assertEqual(5, now.weekday())
        
        self.assertTrue(calendar.expected_state(now))
        
        now = now.replace(hour=1, minute=0)
        self.assertTrue(calendar.expected_state(now))
        
        now = now.replace(hour=1, minute=1)
        self.assertFalse(calendar.expected_state(now))
        
        # Sunday night very late => Monday evening
        now:datetime.datetime = datetime.datetime(2023, 12, 25, 0, 1, 0)
        self.assertEqual(0, now.weekday())
        self.assertFalse(calendar.expected_state(now))
        
        
        