# Pédagogie du Gateway dans OpenClaw

Ce document explique le rôle central du **Gateway**, le serveur qui orchestre toutes les communications, gère les sessions et expose le protocole de contrôle d'OpenClaw.

## 1. Le Gateway comme "Control Plane"

Le Gateway n'est pas qu'un simple serveur web. C'est la **tour de contrôle** (Control Plane) de tout l'écosystème. Il assure la liaison entre :
*   Les **Clients** : UI Web, CLI, applications macOS/iOS/Android.
*   Les **Channels** : WhatsApp, Telegram, Discord.
*   Les **Agents** : La logique de réflexion et l'exécution d'outils.
*   Les **Services** : Cron (tâches planifiées), Browser (contrôle de navigateur).

## 2. Démarrage et Cycle de Vie (`server.impl.ts`)

Lorsqu'on lance `openclaw gateway`, plusieurs étapes critiques se succèdent :
1.  **Validation de la Config** : Lecture et migration automatique du fichier `openclaw.json`.
2.  **Authentification** : Génération ou vérification du jeton (token) de sécurité.
3.  **Découverte** : Activation de **Bonjour (mDNS)** pour être visible sur le réseau local et configuration de **Tailscale** pour l'accès distant sécurisé.
4.  **Sidecars** : Lancement des services auxiliaires :
    *   `CronService` : Pour les rappels et tâches de fond.
    *   `BrowserControl` : Pour permettre à l'IA de naviguer sur le web.
    *   `CanvasHost` : Pour le rendu visuel interactif.

## 3. Le Protocole WebSocket

La communication avec le Gateway repose sur un protocole WebSocket bidirectionnel. Ce protocole est divisé en deux catégories définies dans `src/gateway/server-methods-list.ts`.

### Les Méthodes (Requests)
Ce sont des appels de type RPC (Remote Procedure Call). Un client envoie une requête et attend une réponse.
*   **Contrôle** : `config.apply`, `gateway.restart`.
*   **Agents** : `agents.list`, `sessions.reset`.
*   **Interaction** : `chat.send`, `node.invoke`.

### Les Événements (Broadcast)
Le Gateway diffuse des messages en temps réel à tous les clients connectés.
*   **`chat` / `agent`** : Flux de texte et exécution d'outils en cours.
*   **`presence` / `health`** : État de santé du système et des canaux connectés.
*   **`cron`** : Alertes lors du déclenchement d'une tâche planifiée.

## 4. Gestion de la Présence et de la Santé

Le Gateway maintient un état de santé (`health`) global.
*   Il surveille la connexion des canaux (ex: "Est-ce que WhatsApp est toujours lié ?").
*   Il gère la **Présence Système** : si plusieurs instances ou nœuds sont connectés, il synchronise leur état pour que l'agent sache quels outils physiques (caméra, notifications locales) sont disponibles.

## 5. Sécurité et Flux de Données

Le Gateway agit comme une barrière de sécurité :
*   **Rate Limiting** : Protection contre les attaques par force brute sur le token.
*   **Sanitisation** : Il filtre les messages sortants (ex: suppression des tags de directive interne) avant qu'ils n'arrivent sur les plateformes de messagerie.
*   **Approbations (`exec.approval`)** : Si une commande dangereuse est tentée par l'IA, le Gateway met l'exécution en pause et demande une validation humaine via le protocole.

## 6. Résumé pour le Développeur

*   **Point d'Entrée Unique** : Tout passe par le Gateway (port 18789 par défaut).
*   **WebSocket First** : Privilégiez les événements pour une UI réactive.
*   **Orchestrateur** : Le Gateway ne réfléchit pas, il coordonne ceux qui réfléchissent (les Agents) et ceux qui transmettent (les Channels).

---
*Document généré pour la documentation technique d'OpenClaw.*
