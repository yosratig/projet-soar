<<<<<<< HEAD
import time
import os
import django
import re

# Config Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soar.settings")
django.setup()

from alerts.models import Alert

ALERT_FILE = r"C:\Snort\log\alert_fast.log"

if not os.path.exists(ALERT_FILE):
    print("Fichier alert_fast.log non trouvé !")
    exit(1)

print("=== Surveillance Snort → création Alertes Django ===")

# Fonction pour générer un ID unique simple à partir de la ligne Snort
def get_alert_key(line):
    # exemple : extraire le snort_id [1:5000001:1] + src->dst
    match = re.search(r'\[\d+:(\d+):\d+\].*?(\d+\.\d+\.\d+\.\d+) -> (\d+\.\d+\.\d+\.\d+)', line)
    if match:
        snort_id, src, dst = match.groups()
        return f"{snort_id}_{src}_{dst}"
    return line  # fallback

# dictionnaire pour suivre les alertes déjà ajoutées
seen_alerts = set()

with open(ALERT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    f.seek(0, 2)  # aller à la fin du fichier
    while True:
        line = f.readline()
        if not line:
            time.sleep(1)
            continue

        line = line.strip()
        if line == "":
            continue

        key = get_alert_key(line)

        # Vérifier si l'alerte existe déjà
        if key in seen_alerts or Alert.objects.filter(description__contains=key).exists():
            continue

        seen_alerts.add(key)

        # Créer l'alerte
        alert = Alert.objects.create(
            title="Snort Alert",
            description=line,
            status="new",
            assigned_to=None
        )
        print("[ALERTE AJOUTÉE]", alert.description)
=======
import time
import os
import django
import re

# Config Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soar.settings")
django.setup()

from alerts.models import Alert

ALERT_FILE = r"C:\Snort\log\alert_fast.log"

if not os.path.exists(ALERT_FILE):
    print("Fichier alert_fast.log non trouvé !")
    exit(1)

print("=== Surveillance Snort → création Alertes Django ===")

# Fonction pour générer un ID unique simple à partir de la ligne Snort
def get_alert_key(line):
    # exemple : extraire le snort_id [1:5000001:1] + src->dst
    match = re.search(r'\[\d+:(\d+):\d+\].*?(\d+\.\d+\.\d+\.\d+) -> (\d+\.\d+\.\d+\.\d+)', line)
    if match:
        snort_id, src, dst = match.groups()
        return f"{snort_id}_{src}_{dst}"
    return line  # fallback

# dictionnaire pour suivre les alertes déjà ajoutées
seen_alerts = set()

with open(ALERT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    f.seek(0, 2)  # aller à la fin du fichier
    while True:
        line = f.readline()
        if not line:
            time.sleep(1)
            continue

        line = line.strip()
        if line == "":
            continue

        key = get_alert_key(line)

        # Vérifier si l'alerte existe déjà
        if key in seen_alerts or Alert.objects.filter(description__contains=key).exists():
            continue

        seen_alerts.add(key)

        # Créer l'alerte
        alert = Alert.objects.create(
            title="Snort Alert",
            description=line,
            status="new",
            assigned_to=None
        )
        print("[ALERTE AJOUTÉE]", alert.description)
>>>>>>> bffa0f5bb8ba8e59a0482ebc705e9581bf578689
