from flask import Flask, render_template, request, redirect, url_for, session
import os
import string
import openai
import random
import ahocorasick

app = Flask(__name__)
app.secret_key = 'béber-et-léonie'

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Fonctions utilitaires pour les compteurs
def lire_compteur(filename):
    try:
        with open(filename, 'r') as f:
            return int(f.read())
    except:
        return 0

def increment_compteur(filename):
    count = lire_compteur(filename)
    count += 1
    with open(filename, 'w') as f:
        f.write(str(count))
    return count

def total_visites():
    return (
        lire_compteur('compteur_beber.txt') +
        lire_compteur('compteur_leonie.txt') +
        lire_compteur('compteur_morgane.txt') +
        lire_compteur('compteur_math.txt') +
        lire_compteur('compteur_anselme.txt')
    )

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

# ROUTE D'ACCUEIL avec compteur interne
@app.route('/')
def accueil():
    count = total_visites()
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
    count_beber = increment_compteur('compteur_beber.txt')
    if request.method == 'POST':
        question = request.form.get("question", "").strip()
        if question:
            style = random.choice(STYLES_PERSONNAGES)
            tonalite = random.choice(TONALITES)
            
            # Extraire uniquement le nom du personnage (avant la virgule s'il y en a un)
            nom_personnage = style.split(",")[0]

            intro = f"Pour te répondre, Béber convoque {nom_personnage}. Dans un souffle, il murmure :"

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
    return render_template('index.html', answer=answer, intro=intro, visites=count_beber)

# ORACLE MORGANE D'AVALON
@app.route('/morgane', methods=['GET', 'POST'])
def morgane():
    count_morgane = increment_compteur('compteur_morgane.txt')
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
    return render_template('index3.html', answer=answer, intro=intro, visites=count_morgane)

def get_morgane_answer(question, tonalite):
    # Vérifier le nombre de questions
    nb_questions = question.count("?")
    if nb_questions >= 2:
        return "Choisis une seule question, je ne scruterai qu’un seul fil du destin."

    prompt = f"""
    Tu es Morgane d’Avalon, puissante magicienne et sœur du roi Arthur.
    Tu réponds depuis des dimensions lointaines, avec un style lent, grave, légèrement énigmatique.
    Tu tires ta réponse des vibrations du quartz et de l’aléa.

    Règles :
    - Ne jamais utiliser les mots : secret(s), caché(e)(s), enfoui(e)(s), danse, danser.
    - Ta réponse doit tenir en 1 ou 2 phrases maximum.
    - Elle doit être marquée sans ambiguité et franchement par la tonalité suivante : {tonalite}.
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
            temperature=1.2,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return "Morgane ne parvient pas à capter les flux du destin en cet instant."

# ORACLE LÉONIE
@app.route('/leonie', methods=['GET', 'POST'])
def leonie():
    count_leonie = increment_compteur('compteur_leonie.txt')
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
    return render_template('index2.html', answer=answer, intro=intro, visites=count_leonie)

#Oracle MATHS
@app.route("/math")
def math():
    count_math = increment_compteur('compteur_math.txt')
    return render_template('index4.html', visites=count_math)

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
            max_tokens=230,
            temperature=1.2,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return "Léonie ne parvient pas à lire clairement les signes cette fois."

# Charger le dictionnaire français
def charger_dictionnaire():
    with open('french_dictionary.txt', 'r', encoding='utf-8') as f:
        return set(m.strip().lower() for m in f if len(m.strip()) >= 6)

mots_fr = charger_dictionnaire()

# Charger le dictionnaire français et construire l'automate
def charger_automate():
    automaton = ahocorasick.Automaton()
    with open('french_dictionary.txt', 'r', encoding='utf-8') as f:
        for idx, mot in enumerate(f):
            mot_clean = mot.strip().lower()
            if len(mot_clean) >= 6:
                automaton.add_word(mot_clean, (idx, mot_clean))
    automaton.make_automaton()
    return automaton

automate_fr = charger_automate()

def generer_trois_mots():
    sequence = ""
    bloc_length = 100         # on génère plus de lettres à la fois
    longueur_fenetre = 1000   # plus grande fenêtre pour maximiser les chances
    mots_trouves = set()

    while len(mots_trouves) < 3:
        bloc = ''.join(random.choice(string.ascii_lowercase) for _ in range(bloc_length))
        sequence += bloc
        if len(sequence) > 5000:
            sequence = sequence[-5000:]

        fenetre = sequence[-longueur_fenetre:]

        for end_idx, (idx, mot) in automate_fr.iter(fenetre):
            if mot not in mots_trouves:
                mots_trouves.add(mot)
                if len(mots_trouves) >= 3:
                    break

    return list(mots_trouves)

# Route pour Anselme
@app.route('/anselme', methods=['GET', 'POST'])
def anselme():
    count_anselme = increment_compteur('compteur_anselme.txt')
    interpretation = ""
    mots_tires = []
    nom_personne = ""
    historique = session.get('historique_anselme', [])
    
    if request.method == 'POST':
        nom_personne = request.form['nom_personne'] or "l'Inconnu"
        mots_tires = generer_trois_mots()
        prompt = f"""
        Tu es un médium. Trois mots ont été tirés au hasard pour {nom_personne} : {', '.join(mots_tires)}.
        Compose une phrase courte et imagée qui relie ces trois mots.
        Adapte le ton selon la personnalité du locuteur :
        - Si c'est une célébrité connue, inspire-toi légèrement de son style ou de ses idées.
        - Si c'est une personne inconnue, joue simplement sur le ton masculin ou féminin selon le prénom.
        - Si le prénom évoque l'âge (comme 'Mamie', 'Papi'), adopte un ton d'une personne âgée.
        Ne donne pas d'explication, écris seulement la phrase. Tu ne fais que traduire ce que veut dire {nom_personne} et ne délivre pas de message divinatoire.
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        interpretation = response['choices'][0]['message']['content'].strip()

        historique.append(f"{nom_personne} t’envoie... {', '.join(mots_tires)}<br>Anselme comprend... {interpretation}")
        session['historique_anselme'] = historique

    return render_template('index6.html', nom_personne=nom_personne, mots_tires=', '.join(mots_tires), interpretation=interpretation, historique=historique, visites=count_anselme)

@app.route('/anselme/clear', methods=['POST'])
def clear_anselme():
    session['historique_anselme'] = []
    return redirect(url_for('anselme'))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
