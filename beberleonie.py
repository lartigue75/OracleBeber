from flask import Flask, render_template, request
import random

app = Flask(__name__)

# Tonalités possibles
TONALITES = {
    "positive": [
        "Tout porte à croire que tu es sur la bonne voie.",
        "L’avenir semble te sourire, écoute ton intuition.",
        "Les signes sont encourageants, fonce !"
    ],
    "negative": [
        "Ce que je vois n'est pas des plus rassurants...", 
        "Une prudence s’impose. Les symboles sont confus.",
        "Un obstacle invisible semble se dresser devant toi."
    ],
    "mitigee": [
        "C’est flou… Peut-être, peut-être pas.",
        "Je perçois des choses contradictoires.",
        "Les symboles dansent sans se fixer… patience."
    ]
}

# Masques ou styles de personnages
PERSONNALITES = [
    "une Béber exalté, à la limite du délire mystique",
    "un Béber tranquille, avec une sagesse de bistrot",
    "une Léonie habitée, mais douce et simple",
    "une Léonie inspirée, comme sortie d’un rêve éveillé",
    "un Béber en pleine forme, visionnaire et joyeux",
    "une Léonie un peu inquiète, mais bienveillante"
]

@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/voyance', methods=['GET', 'POST'])
def voyance():
    if request.method == 'POST':
        question = request.form['question']
        voyant = request.form['voyant']  # "beber" ou "leonie"

        tonalite_cle = random.choice(list(TONALITES.keys()))
        tonalite_texte = random.choice(TONALITES[tonalite_cle])
        personnage = random.choice(PERSONNALITES)

        intro = f"Pour te répondre, {voyant.capitalize()} convoque {personnage}."
        return render_template(
            'index2.html', 
            voyant=voyant,
            intro=intro, 
            reponse=tonalite_texte
        )

    return render_template('index2.html', voyant=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
