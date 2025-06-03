from flask import Flask, render_template, request
import os
import openai
import random
import re
import openai.error

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Active ou désactive le filtre à banalités
DEBUG_MODE = True

recent_words = []

TONALITES = [
    "positive", "positive", "positive",
    "négative", "négative", "mitigée"
]

STYLES_PERSONNAGES = [
    "Le Chapelier Fou d'Alice au pays des merveilles",
    "Le Chat de Cheshire, mystérieux et ironique",
    "La Reine de Cœur, autoritaire et excessive",
    "La Pythie de Delphes, en transe prophétique",
    "Merlin l'enchanteur, un brin farceur mais sage"
]

MOTS_BANALS = {
    "nuage", "nuages", "chanter", "chantent", "danse", "dansent", "danser",
    "cosmique", "galaxie", "pluie", "ciel", "étoile", "jubile", "acrobat",
    "acrobatique", "tournoie", "fête", "musique", "camarade", "chant", "rythme"
}

def nettoyer_texte(texte):
    mots = re.findall(r"\b\w+\b", texte.lower())
    return set(mots)

def racine_simplifiee(mot):
    return re.sub(r'(es|s|x|nt|er|ent|ant|ique|iques)$', '', mot)

def filtrer_repetitions(texte):
    global recent_words
    mots = nettoyer_texte(texte)
    racines = {racine_simplifiee(mot) for mot in mots}

    for mot in racines:
        if mot in MOTS_BANALS:
            return True
        if any(mot in w or w in mot for w in recent_words):
            return True

    recent_words.extend(racines)
    if len(recent_words) > 60:
        recent_words = recent_words[-60:]
    return False

def get_answer(question):
    for _ in range(6):
        tonalite = random.choice(TONALITES)
        style = random.choice(STYLES_PERSONNAGES)

        prompt = f"""
        Tu es un oracle inspiré par {style}.
        Tu réponds à la question suivante avec une tonalité {tonalite}.
        - Sois bref (1 ou 2 phrases max)
        - Pas de généralités ou banalités
        - Adopte un ton marqué par ton personnage
        - Évite les répétitions ou motifs trop lyriques

        Question : {question}
        Réponds :
        """

        print(f">>> Appel OpenAI : style = {style}, tonalité = {tonalite}")
        print(f">>> Question : {question}")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un oracle incarné par un personnage fantasque ou mystique."},
                    {"role": "user", "content": prompt.strip()}
                ],
                max_tokens=100,
                temperature=1.2,
                timeout=10
            )
            texte = response.choices[0].message['content'].strip()
            print(f">>> Réponse brute : {texte}")

            if DEBUG_MODE:
                return texte

            if not filtrer_repetitions(texte):
                return texte
            else:
                print(">>> Réponse filtrée.")

        except openai.error.OpenAIError as e:
            print(">>> ERREUR OpenAI :", e)
            return "Béber a buggué pendant sa vision (erreur OpenAI)."

        except Exception as e:
            print(">>> ERREUR inconnue :", e)
            return "Béber est dans le cosmos, réponse impossible."

    return "Béber a buggé sur sa boule de cristal."

@app.route('/', methods=['GET', 'POST'])
def oracle():
    answer = None
    if request.method == 'POST':
        question = request.form.get("question", "").strip()
        if question:
            answer = get_answer(question)
    return render_template('index.html', answer=answer)

@app.route('/ping')
def ping():
    return "pong"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
