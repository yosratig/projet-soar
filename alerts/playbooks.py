from .models import Alert

def run_playbook_on_alert(alert: Alert):
    """
    Simule l'exécution d'un playbook d'automatisation L1.
    Tente de résoudre l'alerte automatiquement en fonction de son contenu.
    """
    
    # 1. Définir les mots-clés de résolution automatique
    auto_resolve_keywords = ["test", "maintenance", "false positive", "fp", "simulated"]
    
    title_lower = alert.title.lower()
    description_lower = alert.description.lower()
    
    # 2. Vérifier la présence de mots-clés
    resolved = False
    keyword = ""
    for kw in auto_resolve_keywords:
        if kw in title_lower or kw in description_lower:
            resolved = True
            keyword = kw
            break
            
    # 3. Appliquer la décision
    if resolved:
        alert.status = "resolved"
        alert.playbook_result = f"Résolution automatique réussie. Mot-clé trouvé: '{keyword}'."
    else:
        # Si non résolu, l'alerte passe en 'in_progress' pour l'analyste L1
        if alert.status == "new":
            alert.status = "in_progress"
        alert.playbook_result = "Analyse automatique terminée. Aucune résolution trouvée. Nécessite une intervention L1."
        
    alert.save()
    return alert
