
# Projet_p@ce_31

from elasticsearch import Elasticsearch
from getpass import getpass

password = getpass("Mot de passe Elasticsearch : ")

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", password),
    verify_certs=False
)
try:
    info = es.info()

    print("\n Connexion à Elasticsearch réussie !")
    print("Nom :", info["name"])
    print("Version :", info["version"]["number"])

except Exception as e:
    print("\n Erreur de connexion :")
    print(type(e).__name__)
    print(e)