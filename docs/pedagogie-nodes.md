# Pédagogie des Nodes dans OpenClaw

Ce document explique le concept de **Node** (Nœud), qui permet à OpenClaw d'interagir avec des appareils physiques locaux (macOS, iOS, Android) pour exécuter des actions concrètes dans le monde réel ou sur le système d'exploitation.

## 1. Qu'est-ce qu'un Node ?

Un Node est un appareil physique ou une application compagnon connectée au Gateway. Contrairement aux agents qui sont des entités logiques (réflexion), les Nodes sont des **fournisseurs de capacités physiques**.

*   **macOS Node** : Permet d'exécuter des commandes système (`system.run`), de gérer des fichiers locaux ou d'afficher des notifications.
*   **iOS/Android Nodes** : Permettent à l'IA d'utiliser la caméra, de lire la localisation GPS ou d'afficher le "Canvas" interactif sur un écran mobile.

## 2. Découverte et Connexion

Pour qu'un appareil devienne un Node, il doit se "présenter" au Gateway :
1.  **Bonjour / mDNS** : Le Gateway diffuse sa présence sur le réseau local. L'application mobile (OpenClaw iOS/Android) détecte automatiquement le serveur.
2.  **Appairage (Pairing)** : Un code de sécurité est utilisé pour lier l'appareil au Gateway de manière permanente.
3.  **WebSocket Persistant** : Une fois lié, le Node maintient une connexion WebSocket ouverte.

## 3. Le Registre des Nœuds (`NodeRegistry`)

Le Gateway maintient une liste en temps réel des nœuds connectés via le `NodeRegistry` (`src/gateway/node-registry.ts`).
Lors de la connexion, le Node annonce ses :
*   **Capacités (`caps`)** : ex: "camera", "location", "system-run".
*   **Permissions** : État des autorisations système (ex: accès au micro accordé ou non).

Grâce à cela, l'agent peut savoir dynamiquement si "la caméra de l'iPhone de Jean" est disponible pour une tâche.

## 4. Le Protocole `node.invoke`

L'interaction technique entre l'IA et le Node suit un flux RPC (Remote Procedure Call) :

1.  **Intention de l'IA** : L'agent décide d'utiliser un outil physique (ex: `camera.snap`).
2.  **Requête du Gateway** : Le Gateway envoie un message `node.invoke.request` au Node ciblé via sa WebSocket.
3.  **Exécution Locale (`node-host/invoke.ts`)** :
    *   Sur mobile : L'application ouvre l'appareil photo.
    *   Sur macOS : Le Node exécute une commande via `spawn`.
4.  **Résultat** : Le Node renvoie `node.invoke.result` avec les données (ex: l'image en Base64 ou le texte de sortie de la console).

## 5. Sécurité et Approbations

L'exécution de commandes sur une machine hôte (surtout macOS) est sensible. OpenClaw implémente une politique d'approbation :
*   **Full Access** : Les commandes sont exécutées sans poser de questions (usage personnel).
*   **Approval Mode (`exec.approval`)** : Pour chaque commande sensible, le Gateway met l'action en pause et envoie une notification au propriétaire pour valider ou rejeter l'exécution.

## 6. Résumé pour le Développeur

*   **Extension Physique** : Les Nodes sortent l'IA du "cloud" pour lui donner des mains (fichiers) et des yeux (caméra).
*   **Dynamisme** : Utilisez `node.list` via le protocole pour découvrir les capacités actives.
*   **Isolation** : Les Nodes iOS/Android sont naturellement isolés, tandis que les Nodes macOS nécessitent une surveillance via les politiques d'approbation.

---
*Document généré pour la documentation technique d'OpenClaw.*
