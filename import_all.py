import json
from pathlib import Path
from getpass import getpass

from elasticsearch import Elasticsearch

# CONFIGURATION

INDEX_NAME = "politiques_sanitaires"
DOSSIER_JSON = Path("corpus/document")


# CONNEXION À ELASTICSEARCH


password = getpass("Mot de passe Elasticsearch : ")

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", password),
    verify_certs=False
)

# VÉRIFICATION DE L'INDEX

if not es.indices.exists(index=INDEX_NAME):
    print(f"L'index '{INDEX_NAME}' n'existe pas.")
    print("Lance d'abord create_index.py")
    exit()

print(f"Connexion à l'index '{INDEX_NAME}' réussie.")


# RÉCUPÉRATION DES FICHIERS JSON

fichiers = sorted(DOSSIER_JSON.glob("*.json"))

print(f"\nNombre de fichiers trouvés : {len(fichiers)}")

# IMPORTATION

succes = 0
erreurs = 0

for fichier in fichiers:

    try:

        # --------------------------------------------------------
        # Lecture du fichier JSON

        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Récupération des métadonnées
        

        metadata = data.get("metadata", {})

        titre = metadata.get("titre", "")
        annee = metadata.get("annee")
        source = metadata.get("source", "")
        type_document = metadata.get("type_document", "")

        # Récupération des sections
        

        sections = []
        textes = []

        for section in data.get("contenu", []):

            section_titre = section.get("titre", "")
            section_texte = section.get("texte", "")

            sections.append({
                "titre": section_titre,
                "texte": section_texte
            })

            if section_texte:
                textes.append(section_texte)

        # Construction du texte intégral

        texte_integral = "\n\n".join(textes)

        # Construction du document Elasticsearch

        document = {
            "titre": titre,
            "annee": str(annee).strip() if annee else None,
            "source": source,
            "type_document": type_document,
            "texte_integral": texte_integral,
            "sections": sections
        }

        # ID = nom du fichier
        # Exemple : 01.json → ID "01"

        document_id = fichier.stem

        # Envoi vers Elasticsearch

        es.index(
            index=INDEX_NAME,
            id=document_id,
            document=document
        )

        succes += 1

        print(f"{fichier.name} → {titre}")

    except Exception as e:

        erreurs += 1

        print(f"{fichier.name} → ERREUR")
        print(f"   {e}")


# RAFRAÎCHISSEMENT DE L'INDEX

try:
    es.indices.refresh(index=INDEX_NAME)
    print("\nIndex Elasticsearch actualisé.")
except Exception as e:
    print(f"\nImpossible d'actualiser l'index : {e}")

# VÉRIFICATION DU NOMBRE DE DOCUMENTS

try:

    resultat = es.count(index=INDEX_NAME)
    nombre_documents = resultat["count"]

except Exception as e:

    nombre_documents = "Impossible à déterminer"
    print(f"\nErreur lors du comptage : {e}")

# RÉSUMÉ

print("\n" + "=" * 60)
print("RÉSUMÉ DE L'IMPORTATION")
print("=" * 60)

print(f"Fichiers trouvés        : {len(fichiers)}")
print(f"Importés avec succès    : {succes}")
print(f"Erreurs                 : {erreurs}")
print(f"Documents dans l'index  : {nombre_documents}")

print("=" * 60)

if erreurs == 0:
    print("Importation terminée avec succès !")
else:
    print(f"Importation terminée avec {erreurs} erreur(s).")