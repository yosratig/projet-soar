# alerts/tasks.py
import re
import subprocess
import platform
from celery import shared_task
from django.utils import timezone
from .models import Alert, Playbook

def extract_ip(text):
    """Extrait la première IPv4 valide du texte."""
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    matches = re.findall(ip_pattern, text)
    for ip in matches:
        parts = ip.split('.')
        if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            return ip
    return None

def block_ip_windows(ip):
    safe_ip = ip.replace('.', '_')
    rule_name = f"SOAR_BLOCK_{safe_ip}"
    try:
        # Ajouter la règle
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "add", "rule",
             f"name={rule_name}", "dir=in", "action=block", f"remoteip={ip}"],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        # Vérifier que la règle a été ajoutée
        check = subprocess.run(
            ["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule_name}"],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        if "No rules match" in check.stdout:
            return f"❌ Échec du blocage IP {ip}."
        return f"✅ IP {ip} bloquée via pare-feu Windows."
    except Exception as e:
        return f"❌ Exception : {str(e)}"


@shared_task
def auto_execute_playbook(alert_id):
    try:
        alert = Alert.objects.get(id=alert_id)
        if alert.playbook_executed:
            return {"status": "already_executed"}

        full_text = (alert.title + " " + alert.description).lower()
        src_ip = extract_ip(alert.title + " " + alert.description)

        # 🔍 Log pour debug
        print(f"[DEBUG] Alert ID: {alert_id}")
        print(f"[DEBUG] Full text: {full_text}")
        print(f"[DEBUG] Extracted IP: {src_ip}")

        results = []

        for playbook in Playbook.objects.filter(is_active=True):
            keywords = [k.strip().lower() for k in playbook.trigger_keywords.split(",") if k.strip()]
            if any(kw in full_text for kw in keywords):
                results.append(f"✅ Playbook '{playbook.name}' déclenché.")

                for action in playbook.actions:
                    act_type = action.get("type")
                    if act_type == "block_ip":
                        if not src_ip:
                            msg = "⚠️ Aucune IP valide trouvée à bloquer. Vérifiez le titre/description de l'alerte."
                            results.append(msg)
                        else:
                            if platform.system() == "Windows":
                                msg = block_ip_windows(src_ip)
                                results.append(msg)
                            else:
                                msg = "❌ Blocage IP non supporté sur ce système."
                                results.append(msg)

                    elif act_type == "log":
                        msg = action.get("message", "Action log exécutée.")
                        results.append(msg)

                    elif act_type == "resolve":
                        results.append("Alerte résolue automatiquement.")

                    else:
                        results.append(f"Action traitée : {act_type}")

                # ✅ Mettre à jour l'alerte avec les résultats
                alert.playbook_result = "\n".join(results)
                alert.status = "resolved"
                alert.resolved_at = timezone.now()
                alert.resolved_by_l2 = True
                alert.playbook_executed = True
                alert.save(update_fields=[
                    'playbook_result', 'status', 'resolved_at',
                    'resolved_by_l2', 'playbook_executed'
                ])
                return {"status": "success", "message": alert.playbook_result}

        # ❗ Aucun playbook trouvé
        results.append("❌ Aucun playbook actif ne correspond aux mots-clés de cette alerte.")
        alert.playbook_result = "\n".join(results)
        alert.playbook_executed = True
        alert.save(update_fields=['playbook_result', 'playbook_executed'])
        return {"status": "no_playbook"}

    except Alert.DoesNotExist:
        return {"status": "error", "message": "Alerte introuvable"}