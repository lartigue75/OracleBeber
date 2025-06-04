from flask import Flask, render_template, request, redirect, url_for, session
import os
import openai
import random

app = Flask(__name__)
app.secret_key = 'béber-et-léonie'

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Tonalités communes
TONALITES = [
    "positive", "positive", "positive",
    "négative", "négative",
    "mitigée"
]

# Fichier compteur
COMPTEUR_FILE = "compteur.txt"

def lire_compteur():
    try:
        with open(COMPTEUR_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def incrementer_compteur():
    compteur = lire_compteur() + 1
    with open(COMPTEUR_FILE, 'w') as f:
        f.write(str(compteur))
    return compteur

# ROUTE D'ACCUEIL
def get_visite_count():
    compteur_path = 'compteur.txt'
    if not os.path.exists(compteur_path):
        with open(compteur_path, 'w') as f:
            f.write('0')
    with open(compteur_path, 'r+') as f:
        try:
            count = int(f.read())
        except ValueError:
            count = 0
        count += 1
        f.seek(0)
        f.write(str(count))
        f.truncate()
    return count

# ORACLE BÉBER
STYLES_PERSONNAGES = [
    "Le Chapelier Fou d'Alice au pays des merveilles",
    "Le Chat de Cheshire, mystérieux et ironique",
    "La Reine de Cœur, autoritaire et excessive",
    "La Pythie de Delphes, en transe prophétique",
    "Merlin l'enchanteur, un brin farceur mais sage"
]

@app.route('/beber', methods=['GET', 'POST'])
def beber():
    if request.method == 'POST':
        question = request.form.get("question", "").strip()
        if question:
            style = random.choice(STYLES_PERSONNAGES)
            tonalite = random.choice(TONALITES)
            intro = f"Pour te répondre, Béber convoque {style}.\n{style}, dans un souffle, murmure :"

            prompt = f"""
            Tu es un oracle inspiré par {style}.
            Tu réponds à la question suivante avec une tonalité {tonalite}.
            - Sois bref (1 ou 2 phrases max)
            - Pas de généralités ou banalités
            - Adopte un ton marqué par ton personnage : exagéré, mystérieux, absurde ou inquiétant
            - Évite les répétitions ou les formules creuses
            - Ta collègue s'appelle Léonie
            - Tu ne sais pas si la personne qui pose la question est un homme ou une femme

            Question : {question}
            Réponds :
            """

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Tu es un oracle incarné par un personnage fantasque ou mystique. Tu réponds brièvement et avec un ton tranché."},
                        {"role": "user", "content": prompt.strip()}
                    ],
                    max_tokens=150,
                    temperature=1.2,
                )
                texte = response.choices[0].message['content'].strip()
                session['answer'] = texte
                session['intro'] = intro
            except Exception as e:
                session['answer'] = "Béber s’est emmêlé les neurones (erreur OpenAI)."
                session['intro'] = ""
        return redirect(url_for('beber'))

    answer = session.pop('answer', None)
    intro = session.pop('intro', None)
    return render_template('index.html', answer=answer, intro=intro)

# ORACLE LÉONIE
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

def get_leonie_answer(question):
    tonalite = random.choice(TONALITES)

    prompt = f"""
    Tu es une femme nommée Léonie, intuitive et sensible. Tu ne te prétends pas oracle.
    Tu parles normalement, mais parfois tu reçois des images ou des symboles que tu traduis à ta façon.
    Tu n’es pas sûre de toi, mais tu dis ce qui te vient, sans chercher à convaincre.
    Ta réponse doit avoir une tonalité {tonalite}.
    Réponse brève d'une ou deux phrases.
    Garde une forme intuitive sans trop détailler.
    Ton collègue s'appelle Béber.
    Tu ne sais pas si la personnes qui pose la question est un homme ou une femme.
    
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
            max_tokens=150,
            temperature=1.1,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return "Léonie ne parvient pas à voir clairement pour le moment."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
