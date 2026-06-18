from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
import json
from django.shortcuts import render, redirect
from .models import Alert
from .models import Playbook


# =========================
# DASHBOARD L1
# =========================
@login_required
def l1_dashboard(request):
    alerts = Alert.objects.filter(
        status__in=["new", "in_progress", "resolved"]
    ).order_by("-detected_at")

    stats = {
        "new_count": Alert.objects.filter(status="new").count(),
        "in_progress_count": Alert.objects.filter(status="in_progress").count(),
        "resolved_count": Alert.objects.filter(status="resolved").count(),
        "escalated_count": Alert.objects.filter(status="escalated").count(),
    }

    return render(request, "alerts/l1_dashboard.html", {
        "alerts": alerts,
        "stats": stats
    })


# =========================
# DASHBOARD L2
# =========================
@login_required
def l2_dashboard(request):
    alerts = Alert.objects.filter(
        status__in=["escalated", "under_investigation"]
    ).order_by("-escalated_at").select_related("assigned_to", "escalated_by")

    stats = {
        "escalated_count": Alert.objects.filter(status="escalated").count(),
        "investigation_count": Alert.objects.filter(
            status="under_investigation",
            assigned_to=request.user
        ).count(),
        "resolved_count": Alert.objects.filter(
            status="resolved",
            resolved_by_l2=True
        ).count(),
    }

    return render(request, "alerts/l2_dashboard.html", {
        "alerts": alerts,
        "stats": stats
    })


# =========================
# PRENDRE UNE ALERTE (L1 & L2)
# =========================
@login_required
@require_http_methods(["POST"])
def take_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)

    if alert.assigned_to is not None:
        return JsonResponse({"error": "Alerte déjà assignée"}, status=400)

    # Méthode 1: Vérifier par email (simple)
    user_email = request.user.email.lower()
    
    if "test1" in user_email or "l1" in user_email:
        # Traiter comme L1
        if alert.status != "new":
            return JsonResponse(
                {"error": "L1 peut seulement prendre des alertes nouvelles"},
                status=400
            )
        alert.status = "in_progress"
        
    elif "test2" in user_email or "l2" in user_email:
        # Traiter comme L2
        if alert.status != "escalated":
            return JsonResponse(
                {"error": "L2 peut seulement prendre des alertes escaladées"},
                status=400
            )
        alert.status = "under_investigation"
        
    else:
        # Déterminer par l'URL ou le contexte
        if 'l2' in request.path or 'l2' in request.META.get('HTTP_REFERER', ''):
            # URL contient 'l2' - probablement L2
            if alert.status != "escalated":
                return JsonResponse(
                    {"error": "Cette alerte n'est pas escaladée"},
                    status=400
                )
            alert.status = "under_investigation"
        else:
            # Sinon L1 par défaut
            if alert.status != "new":
                return JsonResponse(
                    {"error": "Cette alerte n'est pas nouvelle"},
                    status=400
                )
            alert.status = "in_progress"

    alert.assigned_to = request.user
    alert.assigned_at = timezone.now()
    alert.save()

    return JsonResponse({"status": "success", "message": "Alerte prise en charge"})


# =========================
# RÉSOUDRE UNE ALERTE (L1)
# =========================
@login_required
@require_http_methods(["POST"])
def resolve_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)

    if request.user.role != "L1":
        return JsonResponse({"error": "Action réservée au L1"}, status=403)

    alert.status = "resolved"
    alert.resolved_at = timezone.now()
    alert.save()

    return JsonResponse({"status": "success", "message": "Alerte résolue"})


# =========================
# ESCALADER UNE ALERTE (L1)
# =========================
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def escalate_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)

    if alert.status != "in_progress":
        return JsonResponse(
            {"error": "Seules les alertes en cours peuvent être escaladées"},
            status=400
        )

    data = json.loads(request.body)
    alert.status = "escalated"
    alert.escalation_reason = data.get("reason", "Non spécifié")
    alert.severity = data.get("priority", "medium")
    alert.escalated_by = request.user
    alert.escalated_at = timezone.now()
    alert.assigned_to = None

    alert.save()

    return JsonResponse({"status": "success", "message": "Alerte escaladée"})


# =========================
# RÉSOUDRE UNE ALERTE ESCALADÉE (L2)
# =========================
@login_required
@require_http_methods(["POST"])
def resolve_escalated_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)

    if alert.status != "under_investigation":
        return JsonResponse({"error": "Alerte non en investigation"}, status=400)

    if alert.assigned_to != request.user:
        return JsonResponse({"error": "Alerte non assignée à vous"}, status=403)

    alert.status = "resolved"
    alert.resolved_at = timezone.now()
    alert.resolved_by_l2 = True
    alert.save()

    return JsonResponse({"status": "success", "message": "Alerte résolue par L2"})


# =========================
# PLAYBOOKS (STUB)
# =========================
@login_required
def create_playbook(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        playbook_type = request.POST.get("playbook_type", "defense")
        trigger_keywords = request.POST.get("trigger_keywords", "")
        actions = request.POST.get("actions", "[]")  # JSON sous forme de texte

        # Convertir actions en liste Python
        import json
        try:
            actions_list = json.loads(actions)
        except json.JSONDecodeError:
            messages.error(request, "Format JSON invalide pour les actions")
            return render(request, "alerts/create_playbook.html")

        # Créer le playbook
        Playbook.objects.create(
            name=name,
            description=description,
            playbook_type=playbook_type,
            trigger_keywords=trigger_keywords,
            actions=actions_list,
            is_active=True
        )

       
        return redirect("alerts:playbook_list")


    # Si GET, afficher le formulaire
    return render(request, "alerts/create_playbook.html")


@login_required
def playbook_list(request):
    # Récupère tous les playbooks actifs
    playbooks = Playbook.objects.filter(is_active=True)

    return render(request, "alerts/playbook_list.html", {
        "playbooks": playbooks
    })


@login_required
def delete_playbook(request, playbook_id):
    if request.method == "POST":
        try:
            playbook = Playbook.objects.get(id=playbook_id)
            playbook.delete()  # supprime réellement de la base
            return JsonResponse({"status": "success", "message": "Playbook supprimé"})
        except Playbook.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Playbook introuvable"})
    return JsonResponse({"status": "error", "message": "Méthode non autorisée"})


