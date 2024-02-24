
import traceback
from typing import Any
from datetime import datetime

NAMED_CONDITIONS: dict[str, str] = {
    "MORNING": "datetime.now().hour>5 and  datetime.now().hour < 12",
    "DAY": "datetime.now().hour>5 and  datetime.now().hour < 20",
    "EVENING":  "datetime.now().hour>18 and  datetime.now().hour < 24",
    "NIGHT":  "datetime.now().hour>20 or datetime.now().hour < 5",
    "WEEKEND":  "datetime.now().weekday()>4",
    "WEEK":  "datetime.now().weekday()<5",
}

def eval_condition(condition:str) -> bool:
    
    if condition is None:
        return True
    
    condition = condition.strip()
    if len(condition)==0:
        return True
    
    res: bool | None = eval_expression(condition)
    
    if res is None:
        return False
    return res

def eval_expression(code:str) -> bool | None :
    
    # init context
    globals_d:dict[str, Any] = {}
    locals_d:dict[str, Any] = {}
    
    globals_d["datetime"] = datetime
    locals_d["result"] = None 
    
    # resolved named conditions
    code = code.strip()
    if code.upper() in NAMED_CONDITIONS.keys():
        code = NAMED_CONDITIONS[code.upper()]

    # add result wrapper
    code = f"result={code}"
    
    try:
        exec(code, globals_d, locals_d)   
        return locals_d["result"]
    except Exception as e:
        print(traceback.format_exc)
        print(e)
        return None

    
if __name__ == "__main__":
    print(eval_expression("week"))
    print(eval_expression("weekend"))   