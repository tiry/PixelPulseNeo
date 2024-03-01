from typing import Any
import time
import argparse
from Matrix import config
import datetime

USE_GPIO:bool = False

power_control:Any | None = None
try:
    from gpiozero import LED
    power_control = LED(config.POWER_CONTROL_GPIO_PIN)
    USE_GPIO = True
except Exception as e:
    pass

def on():
    if power_control is None:
        print("No GPIO Power Control skiping ON ")
        return
    if not config.POWER_SWITCH_NORMALY_ON:
        power_control.on()
    else:
        power_control.off()
   
def off():
    if power_control is None:
        print("No GPIO Power Control skiping OFF ")
        return
    if config.POWER_SWITCH_NORMALY_ON:
        power_control.on()
    else:
        power_control.off()
   

DAYS: list[str] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] 

class OnOffCalendar():
    
    
    def __init__(self, schedule_template:dict[str, tuple[str,str]]={}) -> None:
        
        schedule:dict[str, tuple[str,str]] = {} 
        for day in DAYS:
            if day in schedule_template:
                schedule[day] = schedule_template[day]
            else:
                schedule[day] = ("8:00", "22:00")        
        self.schedule:dict[str, tuple[str,str]] = schedule
        
    
    def _get_day(self, now:datetime.datetime) -> str:
        
        day_str: str = now.strftime("%A")
        
        # 0+ 6AM count on the dayh before 
        if now.time().hour< 6 and (now.time().hour >0 or now.time().minute >0):
            #print(f"Day Shifting !!!! {day_str}")
            idx: int =  DAYS.index(day_str)
            idx = (idx - 1) % len(DAYS)
            day_str = DAYS[idx]
            #print(f"=> {day_str}")
           
        return day_str
    
    def is_time_between(self, begin_time: datetime.time, end_time: datetime.time, check_time: datetime.time):
        # If check time is not given, default to current local time
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else: # crosses midnight
            return check_time >= begin_time or check_time <= end_time        

    def expected_state(self, now: datetime.datetime| None=None) -> bool:
        if now is None:
            now = datetime.datetime.now()
        day:str = self._get_day(now)
        
        start_time_str: str = self.schedule[day][0]
        end_time_str: str = self.schedule[day][1]
        start_time: datetime.datetime = datetime.datetime.strptime(start_time_str, "%H:%M")
        end_time: datetime.datetime = datetime.datetime.strptime(end_time_str, "%H:%M")
        
        if self.is_time_between(start_time.time(), end_time.time(), now.time()):
            return True
        else: 
            return False

if __name__=="__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--on", help="turns on", action="store_true")
    parser.add_argument("--off", help="turns off", action="store_true")
    parser.add_argument("--test", help="runs test", action="store_true")
 
    args = parser.parse_args()

    if args.on:
        print("Turn Power ON")
        on()
        time.sleep(5)
        print("done, exiting")
    if args.off:
        print("Turn Power OFF")
        off()
        time.sleep(5)
        print("done, exiting")
    if args.test:
        print("Turn Power ON for 2s")
        on()
        time.sleep(2)
        print("Turn Power ON for 3s")
        off()
        time.sleep(3)
        print("Turn Power ON for 4s")
        on()
        time.sleep(4)
        print("Turn Power Off for 1s")
        off()
        time.sleep(1)
        
 