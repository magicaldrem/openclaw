---
name: aegis-crm
description: "Accès au CRM Aegis pour la gestion des clients et des soldes. Utilisez ce skill pour vérifier le solde d'un client. Requiert l'identifiant du canal (numéro de téléphone)."
metadata: { "openclaw": { "emoji": "🏦", "requires": { "bins": ["python3"] } } }
---

# Aegis CRM Skill

Ce skill permet d'interagir avec le CRM interne d'Aegis pour récupérer des informations financières sur les clients.

## Utilisation

✅ **UTILISEZ ce skill quand :**

- Le client demande son solde actuel.
- Vous avez besoin de confirmer l'identité d'un client via son numéro.
- Le client pose des questions sur ses comptes.

❌ **NE PAS UTILISER ce skill quand :**

- Le client demande des informations non financières.
- Vous n'avez pas accès à l'identifiant du canal (phone_id).

## Commandes

### Vérifier le solde (checkBalance)

L'identifiant du client est généralement fourni dans le contexte de la session (ex: le numéro WhatsApp).

```bash
# Vérifier le solde pour un identifiant donné
python3 skills/aegis-crm/crm_api.py checkBalance "33612345678"
```

## Note pour l'Agent

L'identifiant de l'utilisateur (JID ou numéro) est disponible dans vos variables de contexte de message. Si vous ne le trouvez pas, demandez poliment au client son numéro de compte ou de téléphone.
