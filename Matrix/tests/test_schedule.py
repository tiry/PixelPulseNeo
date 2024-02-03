import unittest
from Matrix.driver.base_executor import Scheduler
from Matrix.models.Commands import ScheduleCatalog
from Matrix.driver.executor import CommandEntry,Schedule

import tempfile
import os
import json

PLAYLIST_NAME = "default_test_schedule"

class TestSchedule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix=".json", prefix="schedule-")
        #print("Temporary file created at:", temp_file.name)

        cls.temp_file_name = temp_file.name

        # Create schedule for test
        data = {
                "playlists": {
                    "default": {
                        "commands": [
                            {
                                "command_name": "mta",
                                "duration": 10,
                                "args": [],
                                "kwargs": {}
                            },
                            {
                                "command_name": "meteo",
                                "duration": 10,
                                "args": [],
                                "kwargs": {}
                            },
                        ],
                        "conditions": []
                    },
                    "bitou": {
                        "commands": [
                            {
                                "command_name": "meteo",
                                "duration": 10,
                                "args": [],
                                "kwargs": {}
                            },
                        ],
                        "conditions": []
                    }
                }
            }

        # Write JSON data to the file
        json.dump(data, temp_file)
        temp_file.flush()  # Ensure data is written to the file
        temp_file.close()
        cls.temp_file = temp_file

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.temp_file_name)
        #print("Temporary file deleted:", cls.temp_file_name)

    def test_create_scheduler(self):
        
        scheduler = Scheduler(schedule_file=None)
        schedule = scheduler.get_current_stack()
        #print(f"current schedule = {schedule}")
        self.assertEqual(0, len(schedule.commands))
        self.assertEqual(0, len(schedule.conditions))

        scheduler.append(CommandEntry(command_name="cmd01"))
        self.assertEqual(1, len(schedule.commands))
        scheduler.append(CommandEntry(command_name="cmd02"))
        self.assertEqual(2, len(schedule.commands))
        self.assertEqual("cmd01", schedule.commands[0].command_name)

        scheduler.append_next(CommandEntry(command_name="cmd00"))
        self.assertEqual(3, len(schedule.commands))
        self.assertEqual("cmd00", schedule.commands[0].command_name)

        #print(f"current schedule = {schedule}")

    def test_update_playlists(self):
        
        scheduler = Scheduler(schedule_file=None)
        schedule = scheduler.get_current_stack()
        scheduler.append(CommandEntry(command_name="cmd01"))
        scheduler.append(CommandEntry(command_name="cmd02"))
        scheduler.append_next(CommandEntry(command_name="cmd00"))
        #print(f"current schedule = {schedule}")

        playlists = scheduler.get_playlist_names()
        self.assertEqual(len(playlists), 0)

        scheduler.create_playlist(PLAYLIST_NAME)
        playlists = scheduler.get_playlist_names()
        self.assertEqual(len(playlists), 1)
        #print(f"playlists => {playlists}")

        schedule = scheduler.get_playlist(PLAYLIST_NAME)
        self.assertEqual(3, len(schedule.commands))
        self.assertEqual("cmd00", schedule.commands[0].command_name)

        cmd = scheduler.fetch_next_command()

        self.assertEqual("cmd00", cmd.command_name)
        # did not modify the catalog entry
        self.assertEqual(3, len(schedule.commands))

        # did modify the current playlist
        schedule = scheduler.get_current_stack()
        self.assertEqual(2, len(schedule.commands))
        self.assertEqual("cmd01", schedule.commands[0].command_name)

        # reload from catalog: should be restored
        scheduler.load_playlist(PLAYLIST_NAME)
        schedule = scheduler.get_current_stack()
        self.assertEqual(3, len(schedule.commands))
        self.assertEqual("cmd00", schedule.commands[0].command_name)

        scheduler = Scheduler(schedule_file=None)
        schedule = scheduler.get_current_stack()
        scheduler.append(CommandEntry(command_name="cmd01"))
        scheduler.append(CommandEntry(command_name="cmd02"))
        scheduler.append_next(CommandEntry(command_name="cmd00"))

    def test_create_playlists(self):
        
        scheduler = Scheduler(schedule_file=None)
        
        # create playlist from the queue
        scheduler.append(CommandEntry(command_name="mta"))
        scheduler.append(CommandEntry(command_name="meteo"))
        scheduler.append(CommandEntry(command_name="citibikes"))
        scheduler.append(CommandEntry(command_name="news"))
        scheduler.create_playlist("default")

        # create a playlist from scratch
        commands=[]
        commands.append(CommandEntry(command_name="meteo"))
        commands.append(CommandEntry(command_name="news"))
        commands.append(CommandEntry(command_name="conway"))
        schedule = Schedule(commands=commands)
        scheduler.save_playlist(schedule, "evening")

        # check that we have 2 schedules in the catalog
        playlists = scheduler.get_playlist_names()
        self.assertEqual(len(playlists), 2)
        #print(f"playlists => {playlists}")

        schedule_file="yo.json"
        scheduler.save(schedule_file)

        with open(schedule_file, 'r') as file:
            yo = json.load(file)
            self.assertEqual(2, len(yo["playlists"].keys()))

        os.remove(schedule_file)
        
    def test_load_playlists(self):

        schedule_file = self.__class__.temp_file_name
        scheduler = Scheduler(schedule_file=schedule_file)
        playlists = scheduler.get_playlist_names()
        self.assertEqual(len(playlists), 2)
        
        stack = scheduler.get_current_stack()
        #print(f"stack {stack}")
        #print(f"stack commands {stack.commands}")

        self.assertIsNotNone(stack)
        self.assertEqual(len(stack.commands), 2)
        self.assertEqual("mta", stack.commands[0].command_name)
        self.assertEqual("meteo", stack.commands[1].command_name)

    def test_loop_playlists(self):

        schedule_file = self.__class__.temp_file_name
        scheduler = Scheduler(schedule_file=schedule_file)
        playlists = scheduler.get_playlist_names()
        self.assertEqual(len(playlists), 2)
        
        stack = scheduler.get_current_stack()

        self.assertEqual(len(scheduler.current_stack.commands), 2)
        
        cmd = scheduler.fetch_next_command()
        self.assertEqual("mta", cmd.command_name)
        self.assertEqual(len(scheduler.current_stack.commands), 1)
        
        cmd = scheduler.fetch_next_command()
        self.assertEqual("meteo", cmd.command_name)
        self.assertEqual(len(scheduler.current_stack.commands), 0)
        
        # it shoud now loop back
        cmd = scheduler.fetch_next_command()
        self.assertEqual("mta", cmd.command_name)

        


        











        

        

if __name__ == '__main__':
    unittest.main()