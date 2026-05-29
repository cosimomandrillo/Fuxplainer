from config import PERSONAS

def get_persona_intro(persona_id):
    p = next((p for p in PERSONAS if p["id"] == persona_id), PERSONAS[0])
    return f"Agisci in qualità di un {p['label']}. Contesto operativo: {p['desc']} Il tuo obiettivo è spiegare l'output di un modello a regole fuzzy a un collega esperto."

def build_prompt(strategy, rules, persona_id=None):
    rules_block = rules

    if strategy == "P1":
        return (
            f"The system has determined that {rules_block}\n\n"
            "These results were obtained using fuzzy terms derived from data collected from patients diagnosed with bipolar disorder. "
            "The data represent low-level acoustic features extracted with OpenSmile, which have been shown to correlate with bipolar disorder states.\n\n"
            "Please create a short descriptive text explaining the cluster characteristics in terms of the latent factors (LFs), "
            "and explain each latent factor by referring to the original acoustic features. "
            "Try to link these patterns to the clinical manifestations of bipolar disorder. "
            "Be discursive, not too verbose but not too brief either, and avoid using bullet points."
        )

    if strategy == "P2":
        intro = get_persona_intro(persona_id)
        return (
            f"Role: {intro}\n\n"
            "Scenario: You are explaining to another psychiatrist how a fuzzy rule-based system is used to interpret "
            "the latent factors (LFs) obtained through NMF analysis of acoustic data from patients diagnosed with bipolar disorder.\n\n"
            f"Contextual Information: The system has determined that {rules_block}\n\n"
            "These fuzzy linguistic terms were derived from low-level acoustic features collected using the OpenSmile toolkit "
            "on clinical recordings from patients with bipolar disorder. "
            "These features have been previously linked to distinct affective states typical of the disorder.\n\n"
            "Write a short, discursive explanation suitable for medical professionals. "
            "The text should describe the cluster characteristics in terms of the latent factors LF1 and LF2, "
            "clarify how each LF maps back to the original acoustic features, "
            "relate the acoustic patterns to clinical manifestations of bipolar disorder, "
            "maintain a clear, professional, and trustworthy tone, "
            "and avoid redundancy, excessive technical detail, or bullet points. "
            "The explanation should strike a balance between clarity and conciseness, avoiding oversimplification "
            "while remaining accessible to psychiatrists without deep technical expertise in AI."
        )

    if strategy == "P3":
        intro = get_persona_intro(persona_id)
        return (
            f"Role: {intro}\n\n"
            "Scenario: You are explaining to another psychiatrist how a fuzzy rule-based system is used to interpret "
            "the latent factors (LFs) obtained through NMF analysis of acoustic data from patients diagnosed with bipolar disorder.\n\n"
            f"Contextual Information: The system has determined that {rules_block}\n\n"
            "These fuzzy linguistic terms were derived from low-level acoustic features collected using the OpenSmile toolkit "
            "on clinical recordings from patients with bipolar disorder. "
            "These features have been previously linked to distinct affective states typical of the disorder.\n\n"
            "Write a short, discursive explanation suitable for medical professionals. "
            "The text should describe the cluster characteristics in terms of the latent factors LF1 and LF2, "
            "clarify how each LF maps back to the original acoustic features, "
            "relate the acoustic patterns to clinical manifestations of bipolar disorder, "
            "maintain a clear, professional, and trustworthy tone, "
            "and avoid redundancy, excessive technical detail, or bullet points. "
            "The explanation should strike a balance between clarity and conciseness, avoiding oversimplification "
            "while remaining accessible to psychiatrists without deep technical expertise in AI.\n\n"
            "After your explanation, include a concise list of key scientific or clinical facts that your reasoning depends on, "
            "so that the resident can verify or further study them independently."
        )

    return (
        f"The system has determined that {rules_block}\n\n"
        "Please create a short descriptive text explaining the cluster characteristics in terms of the latent factors (LFs), "
        "and explain each latent factor by referring to the original acoustic features. "
        "Try to link these patterns to the clinical manifestations of bipolar disorder. "
        "Be discursive, not too verbose but not too brief either, and avoid using bullet points."
    )
