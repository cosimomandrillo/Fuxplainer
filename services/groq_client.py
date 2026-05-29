import requests
from config import GROQ_API_KEY

# URL DELL'ENDPOINT PER GLI LLM
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def query_groq(prompt: str, model_id: str) -> str:
    """Invia il prompt a Groq e restituisce il testo generato."""
    
    # CONTROLLO DI SICUREZZA SULLA PRESENZA DELLA CHIAVE API
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY mancante nel file .env.")

    # CONFIGURAZIONE HEADER PER AUTENTICAZIONE E TIPO DATI
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    
    # PAYLOAD DI RICHIESTA CON PARAMETRI DI GENERAZIONE LLM DERIVATI DA ALBERTO VALERIO
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6, 
        "max_tokens": 1024,
        "top_p": 0.9,
    }

    # ESECUZIONE DELLA CHIAMATA CHIAVE POST CON TIMEOUT MASSIMO DI SICUREZZA
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=75)

    # GESTIONE DEGLI STATI DI ERRORE HTTP RICEVUTI DALL'API
    if not resp.ok:
        try:
            err = resp.json().get("error", {}).get("message", resp.text)
        except Exception:
            err = resp.text
        raise RuntimeError(f"Errore Groq {resp.status_code}: {err}")

    return resp.json()["choices"][0]["message"]["content"]