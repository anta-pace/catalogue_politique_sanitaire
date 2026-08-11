import json
from pathlib import Path
from getpass import getpass

from elasticsearch import Elasticsearch


# Configuration

INDEX_NAME = "politiques_sanitaires"

JSON_FILE = Path("corpus/document/01.json")


# Connexion à Elasticsearch

password = getpass("Mot de passe Elasticsearch : ")

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", password),
    verify_certs=False
)


# Lecture du fichier JSON

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


# Récupération des métadonnées

metadata = data.get("metadata", {})

titre = metadata.get("titre", "")
annee = metadata.get("annee")
source = metadata.get("source", "")
type_document = metadata.get("type_document", "")


# Extraction des sections

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


# Création du texte intégral

texte_integral = "\n\n".join(textes)



# Préparation du document

document = {
    "titre": titre,
    "annee": int(annee) if annee else None,
    "source": source,
    "type_document": type_document,
    "texte_integral": texte_integral,
    "sections": sections
}


# Envoi vers Elasticsearch

response = es.index(
    index=INDEX_NAME,
    document=document
)


# Résultat

print("\n Document importé avec succès !")
print("ID Elasticsearch :", response["_id"])
print("Titre :", titre)
print("Année :", annee)
print("Type :", type_document)