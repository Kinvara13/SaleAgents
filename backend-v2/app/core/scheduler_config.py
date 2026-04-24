"""定时任务调度器配置"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
    return scheduler


def _on_job_event(event):
    if event.exception:
        import logging

        logging.getLogger("apscheduler").error(
            f"定时任务执行失败: job_id={event.job_id}, exception={event.exception}"
        )


def init_scheduler() -> AsyncIOScheduler:
    sched = get_scheduler()
    sched.add_listener(_on_job_event, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
    return sched
