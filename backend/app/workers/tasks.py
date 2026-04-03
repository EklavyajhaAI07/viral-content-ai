from app.workers.celery_app import celery_app, _run_async
from app.services.crew_service import run_full_analyze, run_generate, run_trends

@celery_app.task(bind=True, name="tasks.full_analyze")
def task_full_analyze(self, topic, platform, tone, target_audience, caption="", hashtags=""):
    self.update_state(state="STARTED", meta={"progress": 10})
    result = _run_async(run_full_analyze(topic, platform, tone, target_audience, caption, hashtags))
    return result

@celery_app.task(bind=True, name="tasks.generate")
def task_generate(self, topic, platform, tone, target_audience):
    self.update_state(state="STARTED", meta={"progress": 10})
    result = _run_async(run_generate(topic, platform, tone, target_audience))
    return result

@celery_app.task(bind=True, name="tasks.trends")
def task_trends(self, topic, platform):
    result = _run_async(run_trends(topic, platform))
    return result