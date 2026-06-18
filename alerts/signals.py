# alerts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Alert
from .tasks import auto_execute_playbook


@receiver(post_save, sender=Alert)
def trigger_playbook_on_alert(sender, instance, created, **kwargs):
    """
    Déclenche automatiquement le playbook dès qu'une alerte est créée
    """
    if created and not instance.playbook_executed:
        # S'assurer que l'objet est bien enregistré en base
        transaction.on_commit(
            lambda: auto_execute_playbook.delay(instance.id)
        )
