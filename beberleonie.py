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

# Valeurs des arcanes
valeurs_arcanes = {
    "Le Soleil": 11,
    "Le Monde": 10,
    "L’Étoile": 9,
    "Le Chariot": 8,
    "La Force": 7,
    "L’Amoureux": 6,
    "Le Pape": 5,
    "L’Empereur": 4,
    "L’Impératrice": 3,
    "Le Bateleur": 2,
    "Le Mat": 1,
    "La Papesse": 0,
    "La Tempérance": 0,
    "Le Jugement": 0,
    "La Roue de Fortune": -1,
    "La Justice": -2,
    "L’Ermite": -3,
    "Le Pendu": -4,
    "La Lune": -5,
    "Le Diable": -6,
    "La Mort": -7,
    "La Maison Dieu": -8
}

arcanes = list(valeurs_arcanes.keys())

# ROUTE D'ACCUEIL
@app.route('/')
def accueil():
    compteur_path = 'compteur.txt'
    if not os.path.exists(compteur_path):
        with open(compteur_path, 'w') as f:
            f.write('0')

    # Lire, incrémenter, et réécrire le compteur
    with open(compteur_path, 'r+') as f:
        count = int(f.read() or 0)
        count += 1
        f.seek(0)
        f.write(str(count))
        f.truncate()

    return render_template("accueil.html", visites=count)

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
            - Ta collègue voyante s'appelle Léonie et elle travaille dans une pièce voisine.
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
                    max_tokens=100,
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
            arcane = random.choice(arcanes)
            indice = valeurs_arcanes[arcane]
            intro = f"Léonie ferme les yeux… une carte apparaît : {arcane}."
            answer = get_leonie_answer(question, arcane, indice)
            session['answer'] = answer
            session['intro'] = intro
        return redirect(url_for('leonie'))

    answer = session.pop('answer', None)
    intro = session.pop('intro', None)
    return render_template('index2.html', answer=answer, intro=intro)

def get_leonie_answer(question, arcane, indice):
    prompt = f"""
    Tu es une voyante nommée Léonie, intuitive et sensible. Tu tires une carte du tarot avant de répondre.
    Tu ne te prétends pas infaillible, mais tu partages ce que tu perçois avec sincérité.
    Tu commences par dire que tu vois la carte : {arcane}, dont l'indice de positivité ou négativité est {indice}.
    Tu t’inspires de cette carte pour donner une réponse claire, affirmée, même si elle est prudente ou sombre.
    Tu ne dis jamais au demandeur de suivre son intuition : tu donnes une réponse.
    Ta réponse doit refléter l’ambiance induite par l’indice : plus il est élevé, plus tu es positive et confiante. Plus il est bas, plus tu es sombre ou inquiète.
    Tu t’exprimes simplement, en 1 ou 2 phrases maximum.
    Tu ne sais pas si la personne qui pose la question est un homme ou une femme.
    Ton collègue voyant s'appelle Béber et travaille dans la pièce voisine.

    Question : {question}
    Réponse :
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es Léonie, une voyante douce mais déterminée, qui tire une carte et répond clairement sans détour ni conseils flous."},
                {"role": "user", "content": prompt.strip()}
            ],
            max_tokens=120,
            temperature=1.0,  # légèrement réduit
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return "Léonie ne parvient pas à voir clairement pour le moment."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
