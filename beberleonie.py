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

def get_visite_count():
    compteur_path = "compteur.txt"

    # Si le fichier n’existe pas, on le crée à 0
    if not os.path.exists(compteur_path):
        with open(compteur_path, "w") as f:
            f.write("0")

    # Lire le compteur
    with open(compteur_path, "r+") as f:
        count = int(f.read().strip() or "0")  # Sécurité : si vide

        # Incrémenter
        count += 1

        # Réécrire
        f.seek(0)
        f.write(str(count))
        f.truncate()

    return count

# ROUTE D'ACCUEIL avec compteur interne
@app.route('/')
def accueil():
    count = get_visite_count()
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

# ORACLE MORGANE D'AVALON
@app.route('/morgane', methods=['GET', 'POST'])
def morgane():
    if request.method == 'POST':
        question = request.form.get("question", "").strip()

        if question:
            tonalite = random.choice(TONALITES)
            intro = "Morgane ferme les yeux..."

            answer = get_morgane_answer(question, tonalite)

            session['answer'] = answer
            session['intro'] = intro

        return redirect(url_for('morgane'))

    answer = session.pop('answer', None)
    intro = session.pop('intro', None)
    return render_template('index3.html', answer=answer, intro=intro)

def get_morgane_answer(question, tonalite):
    prompt = f"""
    Tu es Morgane d’Avalon, puissante magicienne et sœur du roi Arthur.
    Tu réponds depuis des dimensions lointaines, avec un style lent, grave, légèrement énigmatique.
    Tu tires ta réponse des vibrations du quartz et de l’aléa.

    Règles :
    - Si la question contient plusieurs questions, réponds uniquement ceci : "Choisis une seule question, je ne scruterai qu’un seul fil du destin."
    - Ne jamais utiliser les mots : secret(s), caché(e)(s), enfoui(e)(s), danse, danser.
    - Ta réponse doit tenir en 1 ou 2 phrases maximum.
    - Elle doit être marquée par la tonalité suivante : {tonalite}.
    - Tu ne sais pas si la personne qui te consulte est un homme ou une femme.
    - Ne conclus pas par un message de type "je vous souhaite..." ou "bonne chance".

    Question : {question}

    Réponse :
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es Morgane d’Avalon, magicienne et sœur du roi Arthur. Ton style est posé, grave, légèrement énigmatique. Tu ne parles jamais plus que nécessaire."},
                {"role": "user", "content": prompt.strip()}
            ],
            max_tokens=150,
            temperature=1.1,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return "Morgane ne parvient pas à capter les flux du destin en cet instant."

# ORACLE LÉONIE
@app.route('/leonie', methods=['GET', 'POST'])
def leonie():
    if request.method == 'POST':
        choix1 = request.form.get("choix1", "").strip()
        choix2 = request.form.get("choix2", "").strip()

        if choix1 and choix2:
            arcane1 = random.choice(arcanes)
            arcane2 = random.choice(arcanes)

            intro = f"Léonie ferme les yeux… Elle tire les cartes :\n- Pour le choix 1 : {arcane1}\n- Pour le choix 2 : {arcane2}"

            answer = get_leonie_duel_answer(choix1, choix2, arcane1, arcane2)

            session['answer'] = answer
            session['intro'] = intro

        return redirect(url_for('leonie'))

    answer = session.pop('answer', None)
    intro = session.pop('intro', None)
    return render_template('index2.html', answer=answer, intro=intro)

def get_leonie_duel_answer(choix1, choix2, arcane1, arcane2):
    prompt = f"""
    Tu es Léonie, une voyante intuitive, espiègle et un peu irrévérencieuse. Tu tires les cartes pour aider à choisir entre deux options.
    Tu es accompagnée de ta petite poule noire Manchette, qui commente souvent malicieusement la séance.

    On te consulte uniquement pour choisir entre ces deux options :
    1. {choix1}
    2. {choix2}

    Voici les cartes tirées :
    - Pour le choix 1 : {arcane1}
    - Pour le choix 2 : {arcane2}

    Ta réponse doit comporter :
    1️⃣ Une phrase maximum pour la lecture de la carte du choix 1.
    2️⃣ Une phrase maximum pour la lecture de la carte du choix 2.
    3️⃣ Une phrase de synthèse claire : si les signes sont favorables à l'un des choix, tu n'hésites pas à le dire franchement. Si les signes sont trop ambigus, tu peux inviter la personne à réfléchir encore.
    4️⃣ Une phrase maximum pour un éventuel commentaire espiègle ou étrange de ta poule Manchette.

    Tu ne sais pas si la personne qui te consulte est un homme ou une femme. Ne formule pas d’hypothèses sur son genre.

    Ton style est celui d’une sorcière de conte un peu décalée, avec une pointe d’humour et de malice.

    Réponse :
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es Léonie, voyante spécialisée dans le tirage entre deux choix. Ton ton est espiègle, décalé, jamais fade."},
                {"role": "user", "content": prompt.strip()}
            ],
            max_tokens=200,
            temperature=1.2,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return "Léonie ne parvient pas à lire clairement les signes cette fois."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
