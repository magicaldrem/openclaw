# Pédagogie des Channels et du Routage dans OpenClaw

Ce document explique comment OpenClaw unifie les différentes plateformes de messagerie (WhatsApp, Telegram, Discord, etc.) et comment les messages entrants sont routés vers les bons agents.

## 1. Le Concept de Channel

Un **Channel** dans OpenClaw est un pont entre une plateforme de messagerie externe et le moteur d'IA. Pour éviter de dupliquer la logique pour chaque plateforme, OpenClaw utilise une abstraction appelée **Channel Dock**.

### Le Channel Dock (`src/channels/dock.ts`)
Chaque canal implémente un "Dock" qui définit :
*   **Capacités (`capabilities`)** : Supporte-t-il les images ? Les réactions ? Les sondages ? Le streaming de messages ?
*   **Adaptateurs de Config** : Comment extraire et formater les identifiants (ex: transformer `+33123456789` en format normalisé).
*   **Gestion des Groupes** : Définit si l'agent doit être mentionné pour répondre ou s'il peut lire tous les messages.

## 2. Le Mécanisme de Routage (Routing)

Lorsqu'un message arrive, OpenClaw doit répondre à deux questions :
1.  **Quel Agent** doit répondre ?
2.  **Quelle Session** utiliser pour garder l'historique ?

### Sélection de l'Agent (`resolve-route.ts`)
OpenClaw utilise un système de **Bindings** (liens) défini dans `openclaw.json`. Le routage suit une hiérarchie de priorité (du plus spécifique au plus général) :

1.  **Peer Binding** : Un utilisateur ou un groupe spécifique est lié à un agent.
2.  **Guild/Team Binding** : (Discord/Slack) Un serveur entier est lié à un agent.
3.  **Account Binding** : Tous les messages arrivant sur un compte spécifique (ex: un numéro WhatsApp précis).
4.  **Channel Binding** : Tous les messages d'une plateforme (ex: "tous les Telegram").
5.  **Default** : L'agent par défaut (`main`).

### La Clé de Session (`session-key.ts`)
Pour que l'agent se souvienne de la conversation, chaque échange est lié à une **Session Key**. Elle est construite de manière unique :
`agent:{agentId}:{channel}:{peerKind}:{peerId}`

*Exemple :* `agent:marketing:telegram:group:12345`
Cette clé permet d'isoler parfaitement les conversations : l'agent "Marketing" sur Telegram dans le groupe "A" n'aura pas accès à l'historique du groupe "B".

## 3. Flux d'un Message (Inbound)

1.  **Monitor** : Un processus surveille la plateforme (ex: `telegram/monitor.ts`).
2.  **Ingestion** : Le message est converti en format unifié.
3.  **Routing** : `resolveAgentRoute` détermine l'agent et la `sessionKey`.
4.  **Execution** : Le message est envoyé à l'agent (voir `docs/pedagogie-agents.md`).

## 4. Envoi de Messages (Outbound)

L'agent ne parle pas directement à Telegram. Il utilise des outils de messagerie :
*   **Réponse Directe** : Le texte streamé par l'agent est capturé par le Gateway et renvoyé via l'API de la plateforme.
*   **Outil `message`** : L'agent peut appeler l'outil `message` pour envoyer des messages proactifs, créer des sondages ou ajouter des réactions.
*   **Fragmentation** : Si l'IA génère un texte trop long, le Channel Dock (via `textChunkLimit`) le découpe automatiquement en plusieurs messages pour respecter les limites de la plateforme (ex: 4000 caractères pour Telegram).

## 5. Résumé pour le Développeur

*   **Abstraction** : Le `ChannelDock` uniformise les fonctionnalités des plateformes.
*   **Flexibilité** : Le routage par `bindings` permet de démultiplier les agents sur un même compte.
*   **Continuité** : La `sessionKey` garantit une mémoire cohérente par contexte de discussion.

---
*Document généré pour la documentation technique d'OpenClaw.*
