# Pédagogie des Skills dans OpenClaw

Ce document s'adresse aux développeurs souhaitant comprendre en profondeur comment OpenClaw utilise le concept de **Skill** (compétence) pour étendre les capacités de ses agents IA.

## 1. Qu'est-ce qu'un Skill ?

Dans OpenClaw, un Skill n'est pas simplement un outil ou une fonction. C'est un **paquet auto-contenu de connaissances procédurales**.

Alors qu'un modèle de langage (LLM) possède des connaissances générales, un Skill lui fournit :
*   **Le contexte spécifique** : Schémas de base de données, politiques d'entreprise, documentation d'API.
*   **Les outils d'exécution** : Scripts Python ou Bash pour des tâches déterministes.
*   **Le guide d'utilisation** : Des instructions précises sur *comment* et *quand* utiliser ces ressources.

## 2. Anatomie d'un Skill

Un Skill est un dossier structuré comme suit :

```text
mon-skill/
├── SKILL.md (requis)        # Le cerveau du skill
├── scripts/ (optionnel)     # Code exécutable (Python, JS, Bash...)
├── references/ (optionnel)  # Documentation chargée à la demande
└── assets/ (optionnel)      # Fichiers statiques (templates, images...)
```

### Le fichier SKILL.md
C'est le point d'entrée. Il contient deux parties cruciales :

1.  **Le Frontmatter YAML** : Utilisé par le Gateway pour décider si le skill doit être "montré" à l'agent.
2.  **Le corps Markdown** : Les instructions lues par l'agent une fois que le skill est activé.

Exemple de métadonnées techniques :
```yaml
---
name: mon-outil
description: "Description pour le déclenchement (triggering)"
metadata:
  {
    "openclaw": {
      "requires": {
        "bins": ["ffmpeg"],
        "env": ["API_KEY"]
      }
    }
  }
---
```

## 3. Découverte et Priorité (Discovery)

Le système charge les skills depuis plusieurs emplacements. En cas de conflit de nom, une hiérarchie stricte s'applique (du plus prioritaire au moins prioritaire) :

1.  **Workspace Skills** : `<workspace>/skills` (Spécifique à un projet/agent).
2.  **Agents Skills (Project)** : `<workspace>/.agents/skills`.
3.  **Agents Skills (User)** : `~/.agents/skills`.
4.  **Managed Skills** : `~/.openclaw/skills` (Installés via ClawHub).
5.  **Bundled Skills** : Livrés avec l'application OpenClaw.
6.  **Extra Dirs** : Dossiers configurés manuellement dans `openclaw.json`.

## 4. Cycle de Vie Technique (Deep Dive)

Le moteur de skills d'OpenClaw suit un flux précis pour optimiser l'utilisation de la fenêtre de contexte (Context Window).

### Étape A : Chargement (`loadWorkspaceSkillEntries`)
Le Gateway scanne les répertoires mentionnés ci-dessus. Il ne lit pas encore le contenu complet des fichiers, mais extrait le frontmatter pour chaque dossier contenant un `SKILL.md`.

### Étape B : Filtrage d'Éligibilité (`shouldIncludeSkill`)
C'est ici que la magie technique opère. Pour chaque skill, OpenClaw vérifie :
*   **OS** : Le skill est-il compatible avec le système actuel (darwin, linux, win32) ?
*   **Binaires** (`requires.bins`) : Les outils nécessaires sont-ils présents sur le `PATH` ?
*   **Variables d'environnement** (`requires.env`) : Les clés API nécessaires sont-elles configurées ?
*   **Config** (`requires.config`) : Le skill est-il activé dans `openclaw.json` ?

Si une condition manque, le skill est totalement ignoré pour cette exécution, économisant ainsi des tokens.

### Étape C : Injection dans le Prompt (`buildWorkspaceSkillsPrompt`)
Les skills éligibles sont compilés dans une liste compacte injectée dans le prompt système de l'agent.
*   **Optimisation des chemins** : Les chemins absolus sont transformés en chemins relatifs (`~/...`) pour réduire le nombre de tokens.
*   **Limites de sécurité** : Si trop de skills sont éligibles, OpenClaw les tronque pour éviter de saturer le contexte du LLM.

### Étape D : Exécution et Divulgation Progressive
L'agent ne reçoit initialement que le nom et la description du skill. S'il décide qu'il en a besoin :
1.  Il lit le corps du `SKILL.md`.
2.  Il peut ensuite lire des fichiers dans `references/` ou exécuter des `scripts/`.

Cette approche de **Divulgation Progressive (Progressive Disclosure)** est fondamentale pour permettre à OpenClaw de gérer des centaines de compétences sans perte de performance.

## 5. Commandes Utilisateur et Dispatch

Les skills peuvent également être exposés comme des "Slash Commands" dans les interfaces de chat (Slack, Discord, Telegram).

*   **User Invocable** : Par défaut, un skill `nom-du-skill` devient la commande `/nom-du-skill`.
*   **Command Dispatch** : Un skill peut être configuré pour bypasser l'IA et envoyer les arguments directement à un outil (`command-dispatch: tool`).

## 6. Bonnes Pratiques pour le Développement

*   **Restez concis** : Le LLM est déjà intelligent. Ne documentez que ce qu'il ne peut pas deviner.
*   **Utilisez `references/`** : Si votre documentation dépasse 500 lignes, déportez les détails techniques dans le dossier `references/`.
*   **Testez les binaires** : Utilisez toujours `metadata.openclaw.requires.bins` pour éviter que l'agent n'essaie d'utiliser un outil non installé.

---
*Document généré pour la documentation technique d'OpenClaw.*
