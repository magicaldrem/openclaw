# Aegis : Sécurité et Audit en Entreprise

## 1. Isolation des Sessions (Sandboxing)

Pour protéger l'infrastructure Aegis, chaque session utilisateur (hors administrateur) peut être exécutée dans un environnement Docker isolé.

- **Configuration :** Positionner `agent.sandbox.mode` sur `non-main`.
- **Effet :** Les commandes bash exécutées par les skills ne peuvent pas accéder au système de fichiers de l'hôte Aegis.

## 2. Audit et Traçabilité

Toutes les interactions sont enregistrées pour permettre des audits a posteriori.

- **Chemin des logs :** `~/.openclaw/agents/main/sessions/`
- **Format :** JSONL (une ligne par événement/message).
- **Contenu :** Requête client, outils appelés (ex: `python3 crm_api.py`), données reçues du CRM, et réponse finale de l'IA.

## 3. Confidentialité On-Premise

En utilisant Ollama en local, aucune donnée (numéro de téléphone, solde, historique) n'est envoyée à des tiers.

- **Modèles supportés :** Llama 3, Mistral, Gemma, Phi-3.
- **Flux :** Aegis Gateway <-> Ollama (réseau local uniquement).

## 4. Politique de DM (WhatsApp/Teams)

Par défaut, Aegis utilise une politique de "pairing" pour les nouveaux contacts :

- Un nouveau client reçoit un code de couplage.
- Un administrateur doit approuver le couplage via `openclaw pairing approve`.
- Pour un accès public, changez `dmPolicy` en `open` dans la configuration.
