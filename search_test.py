from getpass import getpass

import urllib3
from elasticsearch import Elasticsearch

# CONFIGURATION

INDEX_NAME = "politiques_sanitaires"

# Désactiver les avertissements HTTPS en local
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# CONNEXION À ELASTICSEARCH

password = getpass("Mot de passe Elasticsearch : ")

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", password),
    verify_certs=False
)

# TEST DE CONNEXION

if not es.ping():
    print("Impossible de se connecter à Elasticsearch.")
    exit()

print("Connexion Elasticsearch réussie.\n")

# RECHERCHE

while True:

    recherche = input(
        "Entrez un mot ou une expression "
        "(ou 'q' pour quitter) : "
    )

    # Quitter
    if recherche.lower() == "q":
        print("Fin de la recherche.")
        break

    # Ignorer une recherche vide
    if not recherche.strip():
        continue

    # RECHERCHE

    resultat = es.search(
        index=INDEX_NAME,
        query={
            "multi_match": {
                "query": recherche,
                "fields": [
                    "titre^3",
                    "texte_integral",
                    "sections.texte"
                ]
            }
        },
        highlight={
            "fields": {
                "texte_integral": {},
                "titre": {}
            }
        },
        size=10
    )

    # NOMBRE DE RÉSULTATS

    total = resultat["hits"]["total"]["value"]

    print("\n" + "=" * 70)
    print(f"Recherche : {recherche}")
    print(f"Nombre de résultats : {total}")
    print("=" * 70)

    if total == 0:
        print("Aucun document trouvé.")
        continue

    # AFFICHAGE DES RÉSULTATS

    for i, hit in enumerate(
        resultat["hits"]["hits"],
        start=1
    ):

        document = hit["_source"]

        print(
            f"\n{i}. "
            f"{document.get('titre', 'Sans titre')}"
        )

        print(
            f"   Année : "
            f"{document.get('annee', '')}"
        )

        print(
            f"   Source : "
            f"{document.get('source', '')}"
        )

        print(
            f"   Type : "
            f"{document.get('type_document', '')}"
        )

        # AFFICHAGE DE L'EXTRAIT SANS <em>

        highlights = hit.get("highlight", {})

        if "texte_integral" in highlights:

            print("   Extrait :")

            extraits = " ... ".join(
                highlights["texte_integral"][:2]
            )

            # Suppression des balises Elasticsearch
            extraits = extraits.replace("<em>", "")
            extraits = extraits.replace("</em>", "")

            print(f"   {extraits}")

        elif "titre" in highlights:

            print("   Correspondance dans le titre :")

            titre = highlights["titre"][0]

            # Suppression des balises <em>
            titre = titre.replace("<em>", "")
            titre = titre.replace("</em>", "")

            print(f"   {titre}")

        else:

            print("   Aucun extrait disponible.")

        print("-" * 70)