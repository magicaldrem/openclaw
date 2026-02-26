# Aegis Architecture (Powered by OpenClaw)

## Introduction

Aegis est une solution de support client intelligente et automatisée, conçue pour être déployée localement (On-Premise) au sein de l'infrastructure d'entreprise. Elle repose sur le socle technique OpenClaw pour l'orchestration des agents, la gestion des canaux de communication et l'exécution de compétences (skills) métier.

## Composants de l'Architecture

### 1. Aegis Gateway (Contrôle et Orchestration)

Le cœur du système, basé sur OpenClaw Gateway.

- **Canaux :** Intégration native avec WhatsApp, Microsoft Teams, Slack, etc.
- **Orchestration :** Routage des messages vers les agents appropriés.
- **Sécurité :** Sandboxing des sessions clients dans des environnements Docker isolés.

### 2. Moteur de Modèle Local (LLM On-Prem)

Pour garantir la souveraineté des données, Aegis utilise des modèles hébergés localement.

- **Technologie :** Ollama ou vLLM.
- **Modèle recommandé :** Llama 3 (8B ou 70B) ou Mistral Nemo.
- **Avantage :** Aucune donnée client (soldes, identifiants) ne quitte le réseau de l'entreprise.

### 3. Skills Métier (Automatisation)

Les "bras" d'Aegis qui interagissent avec les systèmes internes.

- **CRM Connector :** Skill dédié à l'identification du client via son numéro de téléphone.
- **Banking Skill :** Skill spécialisé dans la consultation de solde et l'historique des transactions.

## Flux de données (Exemple "Consultation de solde")

1.  **Réception :** Un client envoie "Mon solde ?" via WhatsApp.
2.  **Identification :** L'Aegis Gateway reçoit le message et le numéro JID (ex: `33612345678@s.whatsapp.net`).
3.  **Contexte :** L'IA locale (Llama 3 via Ollama) analyse l'intention.
4.  **Action :** L'IA appelle le skill `checkBalance`.
5.  **Interrogation :** Le skill effectue une requête sécurisée vers l'API CRM interne avec le JID.
6.  **Réponse IA :** Le skill renvoie le montant (ex: 1250.50€). L'IA formule une réponse naturelle.
7.  **Envoi :** Le message est renvoyé au client sur WhatsApp.

## Déploiement Cible (Docker)

```yaml
version: "3.8"
services:
  aegis-gateway:
    image: openclaw/openclaw:latest
    volumes:
      - ./aegis-config:/home/node/.openclaw
    environment:
      - OPENCLAW_MODE=local
    ports:
      - "18789:18789"
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## Sécurité et Audit

- **Logs d'audit :** Chaque action de skill est enregistrée dans le système de fichiers ou une base SQL pour conformité.
- **Isolation :** Les processus d'exécution bash sont confinés dans des conteneurs éphémères.
