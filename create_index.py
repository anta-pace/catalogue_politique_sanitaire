from elasticsearch import Elasticsearch
from getpass import getpass

# Mot de passe Elasticsearch
password = getpass("Mot de passe Elasticsearch : ")

# Connexion à Elasticsearch
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", password),
    verify_certs=False
)

INDEX_NAME = "politiques_sanitaires"

# Vérifier si l'index existe déjà
if es.indices.exists(index=INDEX_NAME):
    print(f"L'index '{INDEX_NAME}' existe déjà.")
else:
    # Création de l'index avec son mapping
    es.indices.create(
        index=INDEX_NAME,
        mappings={
            "properties": {
                "titre": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },

                "annee": {
                    "type": "keyword"
                },

                "source": {
                    "type": "text"
                },

                "type_document": {
                    "type": "keyword"
                },

                "texte_integral": {
                    "type": "text"
                },

                "sections": {
                    "type": "nested",
                    "properties": {
                        "titre": {
                            "type": "text"
                        },
                        "texte": {
                            "type": "text"
                        }
                    }
                }
            }
        }
    )

    print(f"Index '{INDEX_NAME}' créé avec succès !")