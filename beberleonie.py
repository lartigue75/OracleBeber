from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import os
import openai
import random
import re

app = Flask(__name__)
app.secret_key = 'béber-leonie-oracle'

# Configure OpenAI avec la clé API
openai.api_key = os.environ.get("OPENAI_API_KEY")

recent_words_beber = []

TONALITES = ["positive", "positive", "positive", "négative", "négative", "mitigée"]
STYLES_PERSONNAGES_BEBER = [
    "Le Chapelier Fou d'Alice au pays des merveilles",
    "Le Chat de Cheshire, mystérieux et ironique",
    "La Reine de Cœur, autoritaire et excessive",
    "La Pythie de Delphes, en transe prophétique",
    "Merlin l'enchanteur, un brin farceur mais sage"
]
MOTS_BANALS = {"nuage", "nuages", "chanter", "chantent", "danse", "dansent", "danser", "cosmique", "galaxie", "pluie", "ciel", "étoile", "jubile", "acrobat", "acrobatique", "tournoie", "fête", "musique", "camarade", "chant", "rythme"}

def nettoyer_texte(texte):
    mots = re.findall(r"\b\w+\b", texte.lower())
    return set(mots)

def racine_simplifiee(mot):
    return re.sub(r'(es|s|x|nt|er|ent|ant|ique|iques)$', '', mot)

def filtrer_repetitions_beber(texte):
    global recent_words_beber
    mots = nettoyer_texte(texte)
    racines = {racine_simplifiee(mot) for mot in mots}

    for mot in racines:
        if mot in MOTS_BANALS:
            return True
        if any(mot in w or w in mot for w in recent_words_beber):
            return True

    recent_words_beber.extend(racines)
    if len(recent_words_beber) > 60:
        recent_words_beber = recent_words_beber[-60:]
    return False

def get_answer_beber(question):
    for _ in range(6):
        tonalite = random.choice(TONALITES)
        style = random.choice(STYLES_PERSONNAGES_BEBER)

        intro = f"Pour te répondre, Béber convoque... {style}."

        prompt = f"""
        Tu es un oracle inspiré par {style}.
        Tu réponds à la question suivante avec une tonalité {tonalite}.
        - Sois bref (1 ou 2 phrases max)
        - Pas de généralités ou banalités
        - Adopte un ton marqué par ton personnage : exagéré, mystérieux, absurde ou inquiétant
        - Évite les répétitions ou motifs trop lyriques
        Question : {question}
        Réponds :
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un oracle incarné par un personnage fantasque ou mystique. Tu réponds brièvement et avec un ton tranché, adapté à ta personnalité."},
                    {"role": "user", "content": prompt.strip()}
                ],
                max_tokens=100,
                temperature=1.2,
            )
            texte = response.choices[0].message['content'].strip()
            if not filtrer_repetitions_beber(texte):
                return intro, texte
        except Exception as e:
            return "Béber s’est emmêlé les neurones", f"(erreur OpenAI : {e})"
    return "Béber a buggé sur sa boule de cristal", "..."

def get_leonie_answer(question):
    prompt = f"""
    Tu es une femme nommée Léonie, intuitive et sensible. Tu ne te prétends pas oracle.
    Tu parles normalement, mais parfois tu reçois des images ou des symboles que tu traduis à ta façon.
    Tu n’es pas sûre de toi, mais tu dis ce qui te vient, sans chercher à convaincre.
    
    Question : {question}
    Réponse :
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es Léonie, une femme intuitive qui parle doucement, avec des visions floues qu'elle tente de comprendre."},
                {"role": "user", "content": prompt.strip()}
            ],
            max_tokens=100,
            temperature=1.1,
        )
        texte = response.choices[0].message['content'].strip()
        return texte
    except Exception as e:
        print(">>> ERREUR OpenAI (Léonie):", e)
        return "Léonie ne parvient pas à voir clairement pour le moment."

@app.route('/beber', methods=['GET', 'POST'])
def beber():
    if request.method == 'POST':
        question = request.form.get("question", "").strip()
        if question:
            session['intro'], session['answer'] = get_answer_beber(question)
        return redirect(url_for('beber'))

    intro = session.pop('intro', None)
    answer = session.pop('answer', None)
    return render_template('beber.html', intro=intro, answer=answer)

@app.route('/leonie', methods=['GET', 'POST'])
def leonie():
    if request.method == 'POST':
        question = request.form.get("question", "").strip()
        if question:
            intro = "Léonie ferme les yeux… un symbole lui apparaît."
            answer = get_leonie_answer(question)
            session['answer'] = answer
            session['intro'] = intro
        return redirect(url_for('leonie'))

    answer = session.pop('answer', None)
    intro = session.pop('intro', None)
    return render_template('index2.html', answer=answer, intro=intro)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
