# Pédagogie des Agents dans OpenClaw

Ce document détaille le fonctionnement interne des agents OpenClaw : leur boucle de réflexion, la génération dynamique de leurs prompts et la sécurisation via les sandboxes Docker.

## 1. La Boucle d'Agent (Agent Loop)

Le cœur de l'intelligence d'OpenClaw réside dans une boucle itérative gérée principalement par `runEmbeddedPiAgent` (dans `src/agents/pi-embedded-runner/run.ts`).

### Le cycle d'une itération :
1.  **Réception du Prompt** : Le message utilisateur est reçu via un canal (WhatsApp, Slack, etc.).
2.  **Préparation de l'Attaque (`runEmbeddedAttempt`)** :
    *   Résolution du modèle (Anthropic, OpenAI, Ollama).
    *   Configuration de l'authentification et des clés API.
    *   Initialisation de la session et chargement de l'historique.
3.  **Appel au LLM** : Le prompt système + historique + nouveau message sont envoyés au modèle.
4.  **Action / Réflexion** :
    *   Si le LLM répond du texte : il est streamé vers l'utilisateur.
    *   Si le LLM appelle un **Outil** (Tool Call) : l'agent met la réponse texte en pause.
5.  **Exécution d'Outil** : OpenClaw exécute l'outil (ex: `read`, `exec`, `web_search`).
6.  **Boucle de Retour** : Le résultat de l'outil est réinjecté dans la conversation, et l'agent retourne à l'étape 3 jusqu'à ce que le LLM décide qu'il a terminé (Stop Reason).

### Robustesse et Retries
La boucle gère automatiquement :
*   **Les overflows de contexte** : Si l'historique est trop long, une "compaction" automatique résume les messages passés.
*   **Le failover** : Si un fournisseur d'IA est en panne ou rate-limited, l'agent peut basculer sur un autre profil ou modèle configuré.

## 2. Le Système de Prompt Dynamique

Le "Prompt Système" n'est pas un texte fixe. Il est construit dynamiquement à chaque tour par `buildAgentSystemPrompt` (dans `src/agents/system-prompt.ts`).

### Composition du Prompt :
Le prompt est assemblé par blocs pour donner à l'IA toutes les informations nécessaires à son exécution :

*   **Identité & Soul** : Définit la personnalité de l'agent (souvent via un fichier `SOUL.md`).
*   **Tooling (Outils)** : Liste tous les outils disponibles et explique comment les appeler. Ce bloc est filtré par la politique de sécurité (ex: pas d'accès binaire en sandbox).
*   **Skills (Compétences)** : Injecte les descriptions des skills éligibles (voir `docs/pedagogie-skills.md`).
*   **Workspace & Files** : Indique à l'IA quel est son répertoire de travail et injecte le contenu des fichiers de contexte (ex: `README.md`, schémas).
*   **Runtime Info** : Donne des détails techniques comme l'OS, l'heure actuelle, le fuseau horaire et le modèle utilisé.
*   **Sandbox Info** : Si l'agent est enfermé, le prompt lui explique ses limites (ex: "Vous êtes dans un container Docker").

### Modes de Prompt
Selon le contexte, le prompt peut être :
*   `full` : Pour l'agent principal (toutes les sections).
*   `minimal` : Pour les sous-agents (sections réduites pour économiser des tokens).
*   `none` : Juste l'identité de base.

## 3. Les Sandboxes (Isolation et Sécurité)

OpenClaw utilise Docker pour exécuter des agents dans des environnements isolés, garantissant que l'IA ne peut pas endommager la machine hôte.

### Architecture (`src/agents/sandbox/`)
Lorsqu'un agent tourne en mode sandboxed :
1.  **Container Dédié** : Un container Docker est créé pour la session (ou partagé selon le `scope`).
2.  **Montage de Volumes** : Le répertoire de travail (Workspace) est monté dans le container. OpenClaw gère intelligemment les droits (UID/GID) pour que l'IA puisse écrire dans les fichiers.
3.  **Bridge de Fichiers (`fs-bridge.ts`)** : Même si les outils de shell (`exec`) tournent dans Docker, les outils de fichiers (`read`, `write`) peuvent passer par un "bridge" pour manipuler les fichiers du workspace hôte avec précision.

### Politiques de Sécurité
La configuration `agents.defaults.sandbox.mode` définit quand utiliser une sandbox :
*   `main` : L'agent principal a accès direct à l'hôte (usage personnel).
*   `non-main` : Les sessions dans des groupes ou avec des tiers sont systématiquement enfermées dans Docker.

### Outils Bloqués
Certains outils sont désactivés ou restreints en sandbox :
*   L'outil `gateway` (qui peut redémarrer OpenClaw) est bloqué.
*   L'accès au réseau peut être limité via les règles Docker.
*   L'outil `browser` tourne dans son propre container isolé.

## 4. Résumé pour le Développeur

*   **Boucle** : Itération LLM <-> Exécution d'Outils. Gère les erreurs et la mémoire.
*   **Prompt** : Assemblage de "Project Context" + "Skills" + "Tools" + "Runtime".
*   **Sandbox** : Docker par défaut pour la sécurité multi-utilisateurs.

---
*Document généré pour la documentation technique d'OpenClaw.*
