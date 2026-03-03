# Guide d'Intégration Gmail dans OpenClaw

Ce guide explique comment OpenClaw intègre Gmail pour déclencher des actions d'agent basées sur les e-mails entrants.

## Architecture de l'Intégration

L'intégration Gmail d'OpenClaw ne se connecte pas directement à l'API Gmail via du code Node.js interne. Elle repose sur un écosystème de composants travaillant de concert :

1.  **GogCLI (`gog`)** : Un binaire externe (écrit en Go) qui sert de pont entre l'API Gmail et OpenClaw. Il gère l'authentification OAuth, l'enregistrement des "watches" Gmail et la réception des notifications Push.
2.  **Google Cloud Pub/Sub** : Utilisé par Google pour envoyer des notifications en temps réel lorsqu'un nouvel e-mail arrive.
3.  **Tailscale (Funnel/Serve)** : Fournit un endpoint HTTPS public sécurisé pour recevoir les notifications de Google Pub/Sub, même si votre instance OpenClaw est derrière un pare-feu ou un NAT.
4.  **OpenClaw Gateway (Hooks)** : Reçoit les données formatées par `gog` et les achemine vers les agents appropriés.

## Flux de Données (Pas à Pas)

1.  **Arrivée de l'E-mail** : Un nouvel e-mail arrive dans la boîte de réception Gmail surveillée.
2.  **Notification Google** : Gmail notifie Google Pub/Sub qu'un changement a eu lieu (via le mécanisme `watch`).
3.  **Push Pub/Sub** : Google Pub/Sub envoie un message POST HTTPS à l'endpoint configuré (généralement via Tailscale).
4.  **Réception par `gog`** : Le processus `gog gmail watch serve` reçoit la notification, récupère le contenu de l'e-mail (sujet, expéditeur, corps) via l'API Gmail, et le transmet à la Gateway OpenClaw.
5.  **Traitement par le Hook OpenClaw** : La Gateway reçoit la requête sur `/hooks/gmail`. Le système de **Hooks Mapping** transforme ce payload JSON en un message compréhensible pour l'agent.
6.  **Action de l'Agent** : L'agent reçoit le message (ex: "Nouvel e-mail de X : Sujet Y") et traite la demande selon ses instructions.

## Implémentation dans le Code Source

### 1. Gestion du processus externe (`src/hooks/gmail-watcher.ts`)
OpenClaw maintient un service nommé `GmailWatcher`. Sa responsabilité est de s'assurer que le processus `gog gmail watch serve` est toujours actif.
- Si le processus s'arrête, le Watcher le redémarre automatiquement.
- Il gère également le renouvellement périodique du `watch` Gmail (qui expire toutes les 7 jours par défaut).

### 2. Configuration et Résolution (`src/hooks/gmail.ts`)
Ce fichier définit les types de configuration et la logique pour construire les arguments de ligne de commande envoyés à `gog`.
- `resolveGmailHookRuntimeConfig` : Combine la configuration utilisateur (`openclaw.json`) avec les valeurs par défaut.
- `buildGogWatchServeArgs` : Prépare les arguments pour lancer le serveur de réception de notifications.

### 3. Mappage des Hooks (`src/gateway/hooks-mapping.ts`)
C'est ici que la magie de la transformation opère. OpenClaw possède un "preset" Gmail par défaut :
```typescript
{
  id: "gmail",
  match: { path: "gmail" },
  action: "agent",
  name: "Gmail",
  sessionKey: "hook:gmail:{{messages[0].id}}",
  messageTemplate: "New email from {{messages[0].from}}\nSubject: {{messages[0].subject}}\n{{messages[0].snippet}}\n{{messages[0].body}}",
}
```
Ce template définit comment extraire les informations du JSON envoyé par `gog` pour créer le message final de l'agent.

### 4. Utilitaires de Setup (`src/hooks/gmail-ops.ts` & `gmail-setup-utils.ts`)
Ces fichiers contiennent la logique de l'assistant d'installation (`openclaw webhooks gmail setup`) :
- Vérification des dépendances (`gcloud`, `gog`, `tailscale`).
- Configuration automatique du projet GCP, des topics Pub/Sub et des abonnements.
- Configuration automatique de Tailscale Funnel.

## Configuration (openclaw.json)

L'intégration est activée via la section `hooks` :

```json5
{
  "hooks": {
    "enabled": true,
    "presets": ["gmail"],
    "gmail": {
      "account": "votre-email@gmail.com",
      "model": "anthropic/claude-3-5-sonnet", // Optionnel : modèle spécifique pour Gmail
      "thinking": "low" // Optionnel : niveau de réflexion pour le traitement
    }
  }
}
```

## Points Clés à Retenir

- **Sécurité** : Les webhooks sont protégés par un token (`hooks.token`). Google Pub/Sub communique avec `gog`, qui lui-même communique avec la Gateway OpenClaw en utilisant ce token.
- **Transparence** : OpenClaw utilise `gog` car la gestion des Webhooks Google et du protocole Pub/Sub est complexe à implémenter de manière robuste directement en Node.js.
- **Personnalisation** : Vous pouvez modifier le comportement (ex: quel agent répond, quel message est envoyé) en ajoutant vos propres `mappings` dans la configuration.
