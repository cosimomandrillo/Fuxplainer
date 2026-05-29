import csv
import io
import time
import requests as http_requests
from flask import render_template, request, session, redirect, url_for, jsonify
import config
from services.prompt_manager import build_prompt
from services.metrics import get_metrics_for_ui
from services.groq_client import query_groq

def register_routes(app):
    
    #ROUTING PER LO STEP 1 (CARICAMENTO REGOLE / INPUT TESTUALE)
    @app.route("/", methods=["GET"])
    def step1():
        #MOSTRA LA PAGINA DI INPUT POPOLANDO LA TEXT-BOX CON REGOLE DELLA SESSIONE IN CORSO
        return render_template("step1.html", current_rules=session.get("rules", config.DEFAULT_RULES), step=1)

    @app.route("/step1", methods=["POST"])
    def step1_post():
        #RECUPERA IL TESTO DELLE REGOLE E I FILE CSV CARICATI DALL'UTENTE
        rules = request.form.get("rules", "").strip()
        files = request.files.getlist("csv_files")
        csv_rules = []
        
        #PARSING DEI FILE CSV PER ESTRARRE E PULIRE LE REGOLE RIGA PER RIGA
        for f in files:
            if f and f.filename.endswith(".csv"):
                content = f.read().decode("utf-8", errors="ignore")
                reader = csv.reader(io.StringIO(content))
                for row in reader:
                    line = " ".join(cell.strip() for cell in row if cell.strip())
                    if line: csv_rules.append(line)
        
        #SE SONO PRESENTI REGOLE DA CSV, SOVRASCRIVE IL TESTO MANUALE
        if csv_rules:
            rules = "\n".join(csv_rules)
            
        #SALVATAGGIO IN SESSIONE E REINDIRIZZAMENTO ALLO STEP SUCCESSIVO
        session["rules"] = rules
        return redirect(url_for("step2"))

    #ROUTING PER LO STEP 2 (SELEZIONE STRATEGIA, PERSONA E PREVIEW PROMPT)
    @app.route("/step2", methods=["GET"])
    def step2():
        #RECUPERA LE PREFERENZE CORRENTI O IMPOSTA I VALORI DI DEFAULT
        rules    = session.get("rules", config.DEFAULT_RULES)
        strategy = session.get("strategy", "P1")
        persona  = session.get("persona", "senior_expert")
        
        #COSTRUZIONE DELLA PREVIEW DEL PROMPT IN BASE ALLA STRATEGIA E PERSONA
        prompt_preview = build_prompt(strategy, rules, persona)
        return render_template("step2.html", strategies=config.STRATEGIES, personas=config.PERSONAS, selected_strategy=strategy, selected_persona=persona, prompt_preview=prompt_preview, step=2)

    @app.route("/step2", methods=["POST"])
    def step2_post():
        #SALVATAGGIO IN SESSIONE DI STRATEGIA, PERSONA E PROMPT PERSONALIZZATO DALL'UTENTE
        session["strategy"] = request.form.get("strategy", "P1")
        session["persona"]  = request.form.get("persona", "senior_expert")
        custom_prompt = request.form.get("prompt_preview", "").strip()
        session["custom_prompt"] = custom_prompt if custom_prompt else None
        return redirect(url_for("step3"))

    #ROUTING PER LO STEP 3 (SELEZIONE DEI MODELLI LLM)
    @app.route("/step3", methods=["GET"])
    def step3():
        #RECUPERA I MODELLI SELEZIONATI O IMPOSTA IL PRIMO DELLA LISTA COME DEFAULT
        selected = session.get("selected_models", [config.MODELS[0]["id"]])
        return render_template("step3.html", models=config.MODELS, selected_models=selected, step=3)

    @app.route("/step3", methods=["POST"])
    def step3_post():
        #SALVATAGGIO DEI MODELLI SCELTI DALL'UTENTE IN SESSIONE
        selected = request.form.getlist("models")
        if not selected: selected = [config.MODELS[0]["id"]]
        session["selected_models"] = selected
        return redirect(url_for("step4"))

    #ROUTING PER LO STEP 4 GENERAZIONE
    @app.route("/step4", methods=["GET"])
    def step4():
        #RECUPERO DATI DI CONFIGURAZIONE E PREPARAZIONE DELLE MAPPE DI LABEL PER LA UI
        rules = session.get("rules", config.DEFAULT_RULES)
        strategy = session.get("strategy", "P1")
        persona = session.get("persona", "senior_expert")
        sel_ids = session.get("selected_models", [config.MODELS[0]["id"]])
        
        model_map = {m["id"]: m["label"] for m in config.MODELS}
        persona_map = {p["id"]: p["label"] for p in config.PERSONAS}
        strategy_map = {s["id"]: s["short"] for s in config.STRATEGIES}
        
        selected_models = [{"id": mid, "label": model_map.get(mid, mid)} for mid in sel_ids]
        
        #RENDERING DELLA DASHBOARD FINALE CON TUTTI I PARAMETRI IMPOSTATI
        return render_template(
            "step4.html", rules=rules, strategy=strategy, 
            strategy_label=strategy_map.get(strategy, strategy), 
            persona=persona, persona_label=persona_map.get(persona, persona), 
            selected_models=selected_models, has_api_key=bool(config.GROQ_API_KEY), step=4
        )

    #ENDPOINT API PER LA GENERAZIONE DEL TESTO TRAMITE GROQ
    @app.route("/api/generate", methods=["POST"])
    def api_generate():
        data = request.json or {}
        model_id = data.get("model_id")
        rules = session.get("rules", config.DEFAULT_RULES)
        strategy = session.get("strategy", "P1")
        persona = session.get("persona", "senior_expert")

        #VERIFICA DEI REQUISITI MINIMI DI AUTENTICAZIONE E PARAMETRI
        if not config.GROQ_API_KEY: return jsonify({"error": "GROQ_API_KEY mancante."}), 400
        if not model_id: return jsonify({"error": "Nessun modello specificato."}), 400

        #SCELTA DEL PROMPT (PERSONALIZZATO DALL'UTENTE O COSTRUITO IN AUTOMATICO)
        custom_prompt = session.get("custom_prompt", "")
        prompt = custom_prompt if custom_prompt else build_prompt(strategy, rules, persona)
        t0 = time.time()

        try:
            #CHIAMATA AL CLIENT GROQ E CALCOLO DELLE METRICHE DI PERFORMANCE E COSTO
            output = query_groq(prompt, model_id)
            metrics_ui = get_metrics_for_ui(model_id, 'it', prompt, output, t0)
            
            return jsonify({
                "output": output,
                "metrics": metrics_ui,
                "prompt": prompt,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    #ENDPOINT API PER AGGIORNARE LA PREVIEW DEL PROMPT DINAMICAMENTE NELLA UI
    @app.route("/api/prompt-preview", methods=["POST"])
    def api_prompt_preview():
        data = request.json or {}
        strategy = data.get("strategy", "P1")
        persona = data.get("persona", "senior_expert")
        rules = session.get("rules", config.DEFAULT_RULES)
        return jsonify({"prompt": build_prompt(strategy, rules, persona)})

    #INTEGRAZIONE CON NMF-WEBAPP PER L'IMPORTAZIONE AUTOMATICA DELLE REGOLE FUZZY
    @app.route("/fetch-from-nmf", methods=["GET"])
    def fetch_from_nmf():
        nmf_url = "http://localhost:5000/api/explanations"

        #RICHIESTA HTTP VERSO IL SERVIZIO NMF LOCALE
        try:
            resp = http_requests.get(nmf_url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            #GESTIONE ERRORI DI CONNESSIONE
            error_msg = f"Impossibile contattare nmf-webapp ({nmf_url}): {e}"
            if request.accept_mimetypes.best == "application/json":
                return jsonify({"ok": False, "error": error_msg}), 502
            session["fetch_error"] = error_msg
            return redirect(url_for("step1"))

        #VERIFICA SE IL WORKFLOW NMF HA EFFETTIVAMENTE GENERATO I DATI
        if not data.get("available"):
            error_msg = (
                "nmf-webapp è raggiungibile ma non ha ancora generato "
                "le fuzzy explanations. Completa il workflow NMF fino "
                "alla pagina Fuzzy prima di importare."
            )
            if request.accept_mimetypes.best == "application/json":
                return jsonify({"ok": False, "error": error_msg}), 404
            session["fetch_error"] = error_msg
            return redirect(url_for("step1"))

        #ESTRAZIONE E ACCUMULO DI TUTTE LE DESCRIZIONI (W, H E SAMPLE) DA NMF
        lines = []
        for desc in data.get("w_descriptions", []):
            if isinstance(desc, str) and desc.strip():
                lines.append(desc.strip())
        for desc in data.get("h_descriptions", []):
            if isinstance(desc, str) and desc.strip():
                lines.append(desc.strip())
        for desc in data.get("sample_descriptions", []):
            if isinstance(desc, str) and desc.strip():
                lines.append(desc.strip())

        #SALVATAGGIO DELLE REGOLE ESTRATTE NELLA SESSIONE UTENTE
        rules_text = "\n".join(lines) if lines else ""
        session["rules"] = rules_text
        session["fetch_success"] = (
            f"Importate {len(lines)} regole da nmf-webapp."
        )

        #INVIO RISPOSTA JSON PER RICHIESTE ASINCRONE O REDIRECT ALLA HOME CON STATO AGGIORNATO
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"ok": True, "rules": rules_text, "count": len(lines)})

        return redirect(url_for("step1"))