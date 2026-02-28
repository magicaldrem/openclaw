# Cas Pratique : IA + Base de Données + Accès Contrôlé aux Données

Ce document présente un cas pratique de mise en œuvre d'un projet "Database AI" sécurisé utilisant OpenClaw. Nous allons simuler un scénario où un agent doit accéder à un CRM pour récupérer des données clients et envoyer des emails marketing, tout en gardant un contrôle strict sur les accès.

## 1. Scénario métier

*   **Le Client** : Un tenant d'entreprise active le skill `crm-support`.
*   **La Demande** : "Récupère les emails et les dernières commandes des clients A, B et C dans la base SQL, puis envoie-leur une promotion pour notre nouveau produit."
*   **Contraintes de sécurité** :
    *   L'IA ne doit pas pouvoir supprimer de données dans la DB.
    *   L'envoi d'emails doit être validé manuellement par un humain.

---

## 2. Concepts clés à connaître pour la reproduction

Avant de coder, assurez-vous de maîtriser ces piliers d'OpenClaw (réf: `docs/pedagogie-*.md`) :

1.  **Skills (Modularité)** : Utiliser un skill pour encapsuler les connaissances du CRM (schéma des tables, règles de segmentation).
2.  **Tools (Interfaces)** : Créer ou utiliser des outils spécifiques pour le SQL (`mysql`, `postgres`) et l'emailing.
3.  **Sandboxing (Isolation)** : Exécuter l'agent dans un container Docker où seul l'outil SQL "bridé" est disponible.
4.  **Exec Approvals (Contrôle)** : Configurer une politique d'approbation pour que l'outil d'envoi d'email nécessite une signature humaine.
5.  **Progressive Disclosure** : Ne pas donner tout le contenu de la DB à l'IA d'un coup, mais la laisser interroger via des outils.

---

## 3. Implémentation technique du Skill `crm-support`

### Structure du dossier
```text
skills/crm-support/
├── SKILL.md
├── references/
│   └── db-schema.md      # Documentation des tables SQL
└── scripts/
    └── send_email.py     # Script Python pour l'envoi via API
```

### Extrait de `SKILL.md`
```markdown
---
name: crm-support
description: Permet de consulter les données clients en SQL et d'envoyer des emails de support/marketing.
metadata:
  {
    "openclaw": {
      "requires": {
        "bins": ["python3", "sqlite3"],
        "env": ["SMTP_KEY", "DB_URL"]
      }
    }
  }
---

# Instructions CRM
Vous avez accès à une base de données SQLite.
Consultez [db-schema.md](references/db-schema.md) pour comprendre la structure des tables `customers` et `orders`.

## Procédure d'envoi d'email
Utilisez le script `scripts/send_email.py`.
ATTENTION : Vous devez informer l'utilisateur que l'envoi nécessite une validation.
```

---

## 4. Configuration de l'Accès Contrôlé (Tool-based Access)

Pour garantir que l'IA ne fait pas n'importe quoi, on configure les outils dans `openclaw.json` :

### A. Restriction SQL (Read-Only)
Au lieu de donner l'outil `exec` complet sur l'hôte, on utilise un outil spécifique ou une sandbox.
```json5
// Dans openclaw.json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main" // Tout le support tourne dans Docker
      }
    }
  },
  "tools": {
    "allow": ["read", "exec"], // exec est autorisé mais bridé par la sandbox
  }
}
```

### B. Politique d'Approbation (Human-in-the-loop)
Pour l'envoi d'email (via le script `send_email.py`), on force une approbation manuelle :
```json5
// ~/.openclaw/exec-approvals.json
{
  "allowlist": [
    { "bin": "/usr/bin/sqlite3", "args": ["data.db", "SELECT*"] } // Auto-approuvé pour lecture
  ],
  "ask": "always", // Pour tout le reste, demander à l'humain
  "commands": {
    "python3 scripts/send_email.py": { "ask": "always" }
  }
}
```

---

## 5. Déroulement de l'exécution (Cycle de vie)

1.  **Requête utilisateur** : "Envoie un mail promo aux clients A, B, C."
2.  **Réflexion de l'Agent** :
    *   Il identifie que le skill `crm-support` est éligible.
    *   Il lit `SKILL.md` et `db-schema.md`.
3.  **Action 1 (Lecture)** :
    *   L'IA génère un tool call : `exec("sqlite3 data.db 'SELECT email FROM customers WHERE name IN (A, B, C)'")`.
    *   OpenClaw exécute cela dans la **Sandbox Docker**.
4.  **Action 2 (Calcul)** : L'IA reçoit les emails et prépare les messages.
5.  **Action 3 (Envoi Sensible)** :
    *   L'IA génère : `exec("python3 scripts/send_email.py --to ...")`.
    *   **Blocage du Gateway** : L'outil `exec` détecte une commande sensible.
    *   **Notification** : Vous recevez une demande sur votre UI/Mobile : "Approuver l'envoi d'email ?"
6.  **Finalisation** : Après votre clic "Approuver", le script s'exécute et l'IA confirme : "Emails envoyés avec succès."

---

## 6. Résumé des bénéfices
*   **Sécurité** : La base de données est protégée par l'isolation Docker.
*   **Gouvernance** : Aucune action de sortie (email) ne part sans validation.
*   **Transparence** : Tout le raisonnement de l'IA (choix des clients) est auditable dans l'historique de la session.
