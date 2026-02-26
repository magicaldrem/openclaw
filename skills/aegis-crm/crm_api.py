import sys
import json

# Simulation d'une base de données client
CLIENT_DB = {
    "33612345678": {"name": "Jean Dupont", "balance": 1250.50, "currency": "EUR"},
    "33789456123": {"name": "Alice Martin", "balance": 4500.00, "currency": "EUR"},
    "1234567890": {"name": "Test User", "balance": 0.00, "currency": "USD"}
}

def get_balance(phone_id):
    # Nettoyage de l'identifiant (ex: extraire le numéro du JID WhatsApp)
    clean_id = phone_id.split('@')[0]
    client = CLIENT_DB.get(clean_id)
    if client:
        return {"status": "success", "data": client}
    else:
        return {"status": "error", "message": "Client non trouvé"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Identifiant manquant"}))
        sys.exit(1)

    action = sys.argv[1]
    if action == "checkBalance":
        phone_id = sys.argv[2] if len(sys.argv) > 2 else ""
        print(json.dumps(get_balance(phone_id)))
    else:
        print(json.dumps({"status": "error", "message": "Action inconnue"}))
