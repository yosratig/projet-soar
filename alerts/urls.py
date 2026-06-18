# alerts/urls.py
from django.urls import path
from . import views

app_name = "alerts"

urlpatterns = [
    # =====================
    # DASHBOARDS
    # =====================
    path("l1/", views.l1_dashboard, name="l1_dashboard"),
    path("l2/", views.l2_dashboard, name="l2_dashboard"),

    # =====================
    # PRENDRE UNE ALERTE (L1 & L2)
    # =====================
    path("take/<int:alert_id>/", views.take_alert, name="take_alert"),
    path("l2/take/<int:alert_id>/", views.take_alert, name="l2_take_alert"),

    # =====================
    # ACTIONS
    # =====================
    path("resolve/<int:alert_id>/", views.resolve_alert, name="resolve_alert"),
    path("resolve-l2/<int:alert_id>/", views.resolve_escalated_alert, name="resolve_escalated_alert"),
    path("escalate/<int:alert_id>/", views.escalate_alert, name="escalate_alert"),

    # =====================
    # PLAYBOOKS
    # =====================
    path("playbooks/", views.playbook_list, name="playbook_list"),
    path("playbooks/create/", views.create_playbook, name="create_playbook"),
    path("playbooks/delete/<int:playbook_id>/", views.delete_playbook, name="delete_playbook"),
]
