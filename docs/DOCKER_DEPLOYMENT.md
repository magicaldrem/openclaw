# Guide de Déploiement Aegis On-Premise

Ce guide explique comment déployer Aegis dans votre infrastructure en utilisant Docker et Ollama.

## 1. Structure du projet

```bash
aegis/
├── docker-compose.yml
├── openclaw.json       # Configuration Aegis
└── skills/             # Dossier des compétences métier
    └── aegis-crm/
```

## 2. Fichier Docker-compose (`docker-compose.yml`)

```yaml
version: "3.8"
services:
  aegis:
    image: openclaw/openclaw:latest
    container_name: aegis-gateway
    restart: always
    volumes:
      - ./openclaw.json:/home/node/.openclaw/openclaw.json
      - ./skills:/home/node/.openclaw/workspace/skills
      - aegis_data:/home/node/.openclaw
    ports:
      - "18789:18789"
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    container_name: ollama-service
    volumes:
      - ollama_data:/root/.ollama
    # Décommenter si vous avez une carte NVIDIA
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

volumes:
  aegis_data:
  ollama_data:
```

## 3. Installation et Lancement

1. **Préparer les fichiers :** Copiez les fichiers `openclaw.json` (basé sur `aegis-config.example.json`) et le dossier `skills` dans votre répertoire de travail.
2. **Lancer les services :**
   ```bash
   docker-compose up -d
   ```
3. **Télécharger le modèle LLM :**
   ```bash
   docker exec -it ollama-service ollama run llama3
   ```
4. **Lier WhatsApp :**
   Exécutez la commande de connexion depuis le conteneur Aegis :
   ```bash
   docker exec -it aegis-gateway openclaw channels login
   ```
   Scannez le QR code affiché avec votre téléphone WhatsApp.

## 4. Maintenance

- **Logs :** `docker logs -f aegis-gateway`
- **Mise à jour :** `docker-compose pull && docker-compose up -d`
