from piper_driver.views.projects_view import projects_view
from piper_driver.views.builds_view import builds_view
from piper_driver.views.jobs_view import jobs_view
from piper_driver.views.stages_view import stages_view
from piper_driver.views.webhook_view import webhook_view
from piper_driver.views.runners_view import runners_view
from piper_driver.views.identity_view import identity_view

piper_views = [
    projects_view,
    builds_view,
    jobs_view,
    stages_view,
    webhook_view,
    runners_view,
    identity_view,
]
