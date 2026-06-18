# 🛡️ SOAR – Réponse Automatisée aux Incidents avec Snort

Projet **SOAR (Security Orchestration, Automation and Response)** développé avec **Flutter**, intégrant **Snort** comme moteur de détection d'intrusion (IDS/IPS) et un système de **playbooks automatiques** pour réagir en temps réel aux menaces détectées.

---

## 🎯 Concept du projet

Un SOAR a pour but d'automatiser la réponse aux incidents de sécurité, en réduisant le besoin d'intervention humaine pendant la détection et la réaction initiale à une menace.

Le principe ici repose sur 3 étapes clés :

1. **Détection** 🔍
   Snort surveille le trafic réseau en continu et génère une alerte dès qu'une activité suspecte ou malveillante correspond à une signature/règle connue.

2. **Orchestration automatique** 🤖
   Dès qu'une alerte Snort est levée, le système SOAR l'analyse et déclenche automatiquement le **playbook** correspondant au type de menace détectée — sans action manuelle de l'utilisateur.

3. **Réponse** ⚡
   Le playbook exécute la suite d'actions prédéfinies pour neutraliser ou contenir la menace (selon ce que tu as configuré : blocage, alerte, journalisation, etc.).

L'ensemble du processus est visible et pilotable depuis une interface **Flutter**, qui joue le rôle de tableau de bord (dashboard) pour l'équipe sécurité.

---

## ⚙️ Fonctionnalités principales

- 🔍 Détection des menaces réseau en temps réel via **Snort**
- 🤖 Déclenchement **automatique** d'un playbook dès qu'une alerte est détectée
- 📊 Dashboard Flutter pour visualiser les alertes et incidents en direct
- 🕓 Historique des incidents traités
- 🔁 Logique de réponse personnalisable selon le type de menace

---

## 🏗️ Architecture / Comment ça fonctionne

```
┌─────────────┐      Alerte       ┌──────────────────┐      Déclenche      ┌──────────────┐
│    Snort    │ ─────────────────▶│   Moteur SOAR     │ ───────────────────▶│   Playbook    │
│   (IDS/IPS) │                   │  (Orchestration)   │                      │  (Réponse)    │
└─────────────┘                   └──────────────────┘                      └──────┬───────┘
                                            │                                       │
                                            ▼                                       ▼
                                   ┌──────────────────┐                   Action automatique
                                   │  App Flutter      │                 (blocage, alerte, log…)
                                   │  (Dashboard SOC)  │
                                   └──────────────────┘
```

**Le concept clé : zéro intervention manuelle entre la détection et la première réponse.** L'analyste sécurité supervise via le dashboard, mais la réaction immédiate est entièrement automatisée.

---

## 🛠️ Stack technique

| Composant         | Technologie |
|--------------------|-------------|
| Interface           | Flutter |
| Détection réseau    | Snort (IDS/IPS) |
| Orchestration        | Playbooks automatiques |

---

## 🎥 Démo

Une démonstration vidéo du fonctionnement complet (détection Snort → déclenchement playbook → réponse automatique) est disponible ici :

👉 **[Voir la vidéo de démonstration](https://drive.google.com/file/d/11X1vIgKt-uyapG5DM4Sdbs7F_0nGAuu5/view?usp=sharing)**

---
