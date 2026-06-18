from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.conf import settings
import json

class Alert(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
        ('under_investigation', 'Under Investigation'),  # Ajouté pour L2
    )

    SEVERITY_CHOICES = (  # Ajouté pour la priorité
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Nouveau champ pour la sévérité/priorité
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_alerts'
    )
    
    # NOUVEAUX CHAMPS POUR L'ESCALADE
    escalated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='escalated_alerts'
    )
    
    escalation_reason = models.TextField(null=True, blank=True)
    escalated_at = models.DateTimeField(null=True, blank=True)
    
    # Champs pour le suivi temporel
    assigned_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # AJOUTEZ CETTE LIGNE - Champ pour suivre si résolu par L2
    resolved_by_l2 = models.BooleanField(default=False)
    
    playbook_result = models.TextField(null=True, blank=True) 
    deadline = models.DateTimeField(null=True, blank=True)
    playbook_executed = models.BooleanField(default=False)
    

    def __str__(self):
        return f"Alert #{self.id}: {self.title}"

    def assign_to_L1(self, L1_user, duration_minutes=5):
        self.assigned_to = L1_user
        self.status = "in_progress"
        self.assigned_at = timezone.now()
        self.deadline = timezone.now() + timedelta(minutes=duration_minutes)
        self.save()

    def escalate_to_L2(self, L2_user, escalated_by_user, reason=None, severity='medium'):
        self.assigned_to = L2_user
        self.status = "escalated"
        self.escalated_by = escalated_by_user
        self.escalation_reason = reason
        self.severity = severity  # Priorité d'escalade
        self.escalated_at = timezone.now()
        self.deadline = None
        self.save()
    
    def take_by_L2(self, L2_user):
        """Méthode pour qu'un L2 prenne en charge l'alerte"""
        self.assigned_to = L2_user
        self.status = "under_investigation"
        self.save()
    
    def resolve_by_L2(self):
        """Méthode pour résoudre une alerte par le L2"""
        self.status = "resolved"
        self.resolved_at = timezone.now()
        self.resolved_by_l2 = True  # Ajoutez cette ligne
        self.save()

    class Meta:
        ordering = ['-detected_at']

class Playbook(models.Model):
    """Modèle pour les playbooks de défense créés par les analystes L1."""
    
    PLAYBOOK_TYPE_CHOICES = (
        ('auto_resolve', 'Résolution Automatique'),
        ('defense', 'Défense contre Attaque'),
        ('investigation', 'Investigation'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    playbook_type = models.CharField(max_length=20, choices=PLAYBOOK_TYPE_CHOICES, default='defense')
    
    # Mots-clés pour déclencher le playbook automatiquement
    trigger_keywords = models.TextField(help_text="Mots-clés séparés par des virgules (ex: 'ddos, brute force, injection sql')")
    
    # Actions à exécuter (JSON libre pour les instructions)
    actions = models.JSONField(default=list, help_text="Actions à prendre (format JSON)")
    # Créateur du playbook
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='playbooks'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']