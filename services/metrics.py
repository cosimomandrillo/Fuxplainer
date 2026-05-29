import math
import time
import textstat as ts
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from spacy.lang.en import English
from spacy.lang.it import Italian

# INIZIALIZZAZIONE TOKENIZZATORI LINGUISTICI SPACY PER INGLESE E ITALIANO
nlp_en = English()
nlp_it = Italian()

# CARICAMENTO DEL MODELLO ENCODER PER GLI EMBEDDING TESTUALI
embedder = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def get_metrics_for_ui(model_key, lang, prompt, output, start_time):
    # ASSEGNAZIONE DEL TOKENIZZATORE CORRETTO IN BASE ALLA LINGUA SPECIFICATA
    nlp = nlp_en if lang.lower() == 'en' else nlp_it

    # GESTIONE DI SICUREZZA PER STRINGHE DI OUTPUT VUOTE O MANCANTI (IMPOSTANDO AUTOMATICAMENTE I VALORI A 0.1)
    if not output or not output.strip():
        return {
            "Diversity":      0.1,
            "diversity_MAAS": 0.1,
            "Readability":    0.1,
            "Coherence":      0.1,
            "Coverage":       0.1,
            "coverage_token": 0.1,
            "Time":           0.1,
            "raw_time":       round(float(time.time() - start_time), 2),
        }

    # CALCOLO DIVERSITY (TTR + MAAS) 
    # CONTEGGIO INTEGRALE DI TUTTI I TOKEN
    tokens = [t.text for t in nlp(output)]
    n_tokens = len(tokens)
    n_types  = len(set(tokens))
    if n_tokens > 0 and n_types > 0:
        ttr  = n_types / n_tokens
        maas = (math.log(n_tokens) - math.log(n_types)) / (math.log(n_tokens) ** 2)
    else:
        ttr  = 0.0
        maas = 0.0

    # CALCOLO READABILITY 
    # INDICE FLESCH PER INGLESE O GULPEASE PER ITALIANO, NORMALIZZATO TRA 0.1 E 1.0 PER LA UI
    try:
        readability_raw = ts.flesch_reading_ease(output) if lang.lower() == 'en' else ts.gulpease_index(output)
        readability = max(0.1, min(1.0, readability_raw / 100.0))
    except Exception:
        readability = 0.1

    # CALCOLO COHERENCE 
    # COERENZA LOCALE TRAMITE SIMILARITÀ COSENO DELLA DISTANZA DI EMBEDDING TRA FRASI CONSECUTIVE
    sentences = output.replace('.\n\n', '. ').replace('\n\n', '').replace('\n', '. ').split('. ')
    sentences = [s for s in sentences if s.strip()]
    if sentences:
        try:
            emb = embedder.encode(sentences)
            similarities = [
                cosine_similarity([emb[i]], [emb[i + 1]])[0][0]
                for i in range(len(emb) - 1)
            ]
            coherence_score = sum(similarities) / len(similarities) if similarities else 0.0
        except Exception:
            coherence_score = 0.0
    else:
        coherence_score = 0.0

    # CALCOLO COVERAGE (DUE METRICHE INDIPENDENTI) 
    
    # 1. COVERAGE SEMANTICA (BASATA SU EMBEDDING TRA PROMPT DI RIFERIMENTO E OUTPUT GENERATO)
    reference_texts = prompt.replace('.\n\n', '. ').replace('\n\n', '').replace('\n', '. ').split('. ')
    reference_texts = [s for s in reference_texts if s.strip()]
    if reference_texts and sentences:
        try:
            reference_embeddings = embedder.encode(reference_texts)
            text_embeddings      = embedder.encode([output])
            ref_similarities     = cosine_similarity(text_embeddings, reference_embeddings)
            coverage_embedding_based = sum(ref_similarities[0]) / len(reference_texts)
        except Exception:
            coverage_embedding_based = 0.0
    else:
        coverage_embedding_based = 0.0

    # 2. COVERAGE LESSICALE (INDICE JACCARD SULLE CONTENT WORDS FILTRANDO STOPWORD E PUNTEGGIATURA)
    try:
        text_input  = [t.text.lower() for t in nlp(prompt.replace('\n', ' '))
                       if not (t.is_punct or t.is_stop)]
        text_input  = list(filter(lambda x: x != ' ', text_input))
        text_output = [t.text.lower() for t in nlp(output.replace('\n', ' '))
                       if not (t.is_punct or t.is_stop)]
        text_output = list(filter(lambda x: x != ' ', text_output))
        union_len   = len(set(text_input).union(text_output))
        coverage_token_based = (
            len(set(text_input).intersection(text_output)) / union_len
            if union_len > 0 else 0.0
        )
    except Exception:
        coverage_token_based = 0.0

    # CALCOLO TEMPO 
    # CONVERSIONE DEL TEMPO DI RISPOSTA REALE IN UN PUNTEGGIO NORMALIZZATO [0.1, 1.0]
    elapsed    = time.time() - start_time
    time_score = max(0.1, min(1.0, 1 - (elapsed / 25)))

    # PACCHETTO DATI FINALE DA PASSARE ALLA COMPONENTE RADAR CHART DELLA UI
    return {
        "Diversity":      round(float(ttr), 3),
        "diversity_MAAS": round(float(maas), 4),
        "Readability":    round(float(readability), 3),
        "Coherence":      round(float(coherence_score), 3),
        "Coverage":       round(float(coverage_embedding_based), 3),
        "coverage_token": round(float(coverage_token_based), 3),
        "Time":           round(float(time_score), 3),
        "raw_time":       round(float(elapsed), 2),
    }
    
#CALCOLO DELLE METRICHE FORNITO DA ALBERTO VALERIO, PICCOLA MODIFICA SOLO PER LA NORMALIZZAZIONE DEI RISULTATI VISTO CHE ANDRANNO IN UI