from src.main import get_weather
from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()
@sched.scheduled_job('cron', day_of_week='mon-sun', hour=6)
def scheduled_job():
    print('Start clock')
    get_weather()

sched.start()