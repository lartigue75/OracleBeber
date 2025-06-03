from flask import Flask, render_template, request
import os
import openai
import random
import re
import openai.error

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Mode debug : désactive le filtre à banalités
DEBUG_MODE = True

TONALITES = [
    "positive", "positive", "positive",
    "négative", "négative", "mitigée"
]

STYLES_PERSONNAGES = [
    {
        "nom": "Le Chapelier Fou",
        "intro": "Le Chapelier Fou te répond avec un rictus tremblant :",
    },
    {
        "nom": "Le Chat de Cheshire",
        "intro": "Dans un sourire qui s'efface, le Chat de Cheshire te souffle :",
    },
    {
        "nom": "La Reine de Cœur",
        "intro": "La Reine de Cœur crie depuis son trône instable :",
    },
    {
        "nom": "La Pythie de Delphes",
        "intro": "La Pythie, les yeux révulsés, murmure en transe :",
    },
    {
        "nom": "Merlin l’Enchanteur",
        "intro": "Merlin l’Enchanteur, à moitié endormi, marmonne :",
    }
]

def get_answer(question):
    for _ in range(6):
        tonalite = random.choice(TONALITES)
        style_obj = random.choice(STYLES_PERSONNAGES)
        nom = style_obj["nom"]
        intro = style_obj["intro"]

        prompt = f"""
        Tu es un oracle inspiré par {nom}.
        Tu réponds à la question suivante avec une tonalité {tonalite}.
        - Sois bref (1 ou 2 phrases max)
        - Pas de généralités ou banalités
        - Adopte un ton marqué par ton personnage
        - Évite les répétitions ou envolées lyriques

        Question : {question}
        Réponds :
        """

        print(f">>> OpenAI : {nom} / Tonalité : {tonalite}")
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
            print(f">>> Réponse : {texte}")

            # Affichage final
            final_response = f"Pour te répondre, Béber convoque {nom}.\n{intro}\n« {texte} »"
            return final_response

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
