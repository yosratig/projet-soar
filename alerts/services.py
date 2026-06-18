from .models import Alert, Playbook
from django.utils import timezone

def executer_playbook(playbook, alert):
    """
    Ici tu peux définir ce que fait le playbook.
    Pour commencer, on va juste afficher et résoudre l'alerte.
    """
    # Exemple : afficher l'action
    print(f"Playbook '{playbook.name}' exécuté pour l'alerte {alert.id} ({alert.type})")

    # On peut résoudre automatiquement l'alerte
    alert.status = "resolved"
    alert.resolved_at = timezone.now()
    alert.save()

def traiter_alerte_automatiquement(alert_id):
    """
    Vérifie si un playbook correspond au type d'alerte et l'exécute.
    """
    alert = Alert.objects.get(id=alert_id)

    try:
        # On suppose que le playbook correspond au type d'alerte
        playbook = Playbook.objects.get(trigger_keywords__icontains=alert.type, is_active=True)
    except Playbook.DoesNotExist:
        playbook = None

    if playbook:
        executer_playbook(playbook, alert)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Alert
from .services import traiter_alerte_automatiquement

@csrf_exempt
def snort_webhook(request):
    if request.method == "POST":
        data = request.POST
        alert = Alert.objects.create(
            name=data.get("name", "Alerte Snort"),
            description=data.get("description", ""),
            type=data.get("type", "Inconnu"),
            status="new"
        )

        # ⚡ Traitement automatique si playbook existe
        traiter_alerte_automatiquement(alert.id)

        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "méthode non autorisée"})
