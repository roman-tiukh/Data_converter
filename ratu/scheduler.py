import schedule
import time
from datetime import datetime

def action ():
    now = datetime.now()
    print(datetime.strftime(datetime.now(), "%H:%M:%S"))

# schedule.every(1).seconds.do(action)
schedule.every().day.at("13:34").do(action)
schedule.every().day.at("13:35").do(action)

while 1:
    schedule.run_pending()
    time.sleep(1)
