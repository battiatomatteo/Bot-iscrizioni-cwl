import requests

def main():
    try:
        # Richiesta all'API
        response = requests.get("https://api.warmachine.cc/v1/playerlist")
        response.raise_for_status()

        # La risposta è già una lista di player
        player_list = response.json()

        print("✅ Dati ricevuti. Ecco i primi 10 player:")
        for p in player_list[:10]:
            print(f"- Nome: {p['attacker_name']} | Tag: {p['attacker_tag']} | TH: {p['attacker_th']}")

    except Exception as e:
        print("❌ Errore durante il recupero o la decodifica dei dati:")
        print(e)

if __name__ == "__main__":
    main()
