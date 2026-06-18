from django.db.models.signals import post_save
from django.dispatch import receiver
from  django.db.models import Alert, Playbook
from .tasks import execute_playbook_task

@receiver(post_save, sender=Alert)
def auto_run_playbook(sender, instance, created, **kwargs):
    if not created:
        return

    alert_text = instance.message.lower()
    playbooks = Playbook.objects.filter(is_active=True)

    for playbook in playbooks:
        keywords = [k.strip().lower() for k in playbook.trigger_keywords.split(",")]
        for kw in keywords:
            if kw in alert_text:
                execute_playbook_task.delay(playbook.id, instance.id)
                break
