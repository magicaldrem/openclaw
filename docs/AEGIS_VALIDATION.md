# Aegis Workflow Validation

Ce document décrit comment valider le bon fonctionnement du système Aegis après installation.

## Scénario de Test : Consultation de solde

### Pré-requis

- Aegis Gateway démarré.
- Skill `aegis-crm` installé dans le workspace.
- Compte WhatsApp lié.

### Étapes de validation

1. **Envoi du message (Côté Client)**
   - Envoyer "Bonjour, quel est le solde de mon compte ?" depuis le numéro `+33612345678`.

2. **Traitement (Côté Aegis Gateway)**
   - Vérifier les logs (`tail -f /tmp/openclaw-gateway.log`).
   - L'IA doit identifier l'intention de consultation de solde.
   - L'IA doit appeler l'outil : `python3 skills/aegis-crm/crm_api.py checkBalance "33612345678"`.

3. **Réception du résultat**
   - Le script renvoie : `{"status": "success", "data": {"name": "Jean Dupont", "balance": 1250.5, "currency": "EUR"}}`.

4. **Réponse finale (Côté Client)**
   - L'IA doit répondre : "Bonjour Jean Dupont, le solde de votre compte est actuellement de 1250,50 EUR."

## Test en ligne de commande (Simulation)

Vous pouvez simuler l'exécution du skill directement pour vérifier la connectivité avec le CRM :

```bash
python3 skills/aegis-crm/crm_api.py checkBalance "33612345678"
```

Si vous recevez un JSON avec les données de Jean Dupont, le skill est opérationnel.
