from typing import Any
import time
import argparse
from Matrix import config

USE_GPIO:bool = False

power_control:Any | None = None
try:
    from gpiozero import LED
    power_control = LED(config.POWER_CONTROL_GPIO_PIN)
    USE_GPIO = True
except Exception as e:
    print(e)
    

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
        
 