import sched

from apscheduler.schedulers.blocking import BlockingScheduler

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=6)
def scheduled_job():
    print('This job is run every weekday at 5pm.')

sched.start()