import os
from dotenv import load_dotenv

#FUNZIONE PER CARICARE IL .ENV PRESENTE NELLA ROOT
load_dotenv()

#CARICAMENTO DELL'API KEY E CREAZIONE DELLA CHIAVE DI CRIPTAZIONE
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "fuzzy-llm-xai-secret-key-2024")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

#MODELLI ATTUALMENTE FUNZIONANTI SU GROQ
MODELS = [
    {"id": "llama-3.1-8b-instant",                          "label": "LLaMA 3.1 8B Instant"},
    {"id": "llama-3.3-70b-versatile",                       "label": "LLaMA 3.3 70B Versatile"},
    {"id": "openai/gpt-oss-120b",                           "label": "GPT-OSS 120B"},
    {"id": "openai/gpt-oss-20b",                            "label": "GPT-OSS 20B"},
    {"id": "meta-llama/llama-4-scout-17b-16e-instruct",     "label": "LLaMA 4 Scout 17B"},
    {"id": "qwen/qwen3-32b",                                "label": "Qwen3 32B"},
]

#PERSONAS PER IL PROMPT
PERSONAS = [
    {"id": "Psicologo",   "label": "Psicologo",             "desc": "Esperto nell'analisi dei processi cognitivo-comportamentali, e sul ragionamento umano e clinico"},
    {"id": "Psichiatra",  "label": "Psichiatra",            "desc": "Specialista in psichiatria, focalizzato sull modellazione statistica per l'estrazione di insight clinici predittivi da dati complessi."},
]

#STRATEGIE PER IL PROMPT
STRATEGIES = [
    {"id": "P1", "short": "Zero-Shot",            "desc": "Generazione diretta dalle regole fuzzy, senza indicazioni o contesti aggiuntivi."},
    {"id": "P2", "short": "Persona",              "desc": "L'LLM adotta un ruolo esperto per adattare le spiegazioni al pubblico di destinazione."},
    {"id": "P3", "short": "Persona + Fact-Check", "desc": "Persona esperta + richiesta esplicita di una lista di fatti scientifici verificabili."},
]

DEFAULT_RULES = ""
