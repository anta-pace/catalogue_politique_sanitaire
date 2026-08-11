# Phase 2 — Extraction et structuration du corpus

## Prérequis

```bash
pip install pandas openpyxl requests pdfplumber
```

## Utilisation

Placer `Catalogue_politiques_sanitaires_SN.xlsx` dans le même dossier que le script, puis :

```bash
# Test rapide sur 5 documents avant de tout lancer
python3 extract_corpus.py --catalogue Catalogue_politiques_sanitaires_SN.xlsx --limit 5

# Lancement complet (peut prendre du temps selon le nombre de documents)
python3 extract_corpus.py --catalogue Catalogue_politiques_sanitaires_SN.xlsx

# Si la connexion coupe ou si des documents échouent, relancer seulement les échecs
python3 extract_corpus.py --catalogue Catalogue_politiques_sanitaires_SN.xlsx --retry-failed
```

Le script est **idempotent** : les PDF déjà téléchargés ne sont pas re-téléchargés, tu peux
l'interrompre et le relancer sans tout recommencer.

## Résultat produit

```
corpus/
├── pdfs/                  # PDF originaux (cache local)
├── documents/             # 1 fichier JSON structuré par document (ID.json)
│   ├── SEN-SAN-0001.json
│   ├── SEN-SAN-0002.json
│   └── ...
└── extraction_log.csv     # rapport : succès / échecs / PDF suspects scannés
```

Chaque `documents/{ID}.json` contient toutes les métadonnées normalisées + le texte intégral —
c'est ce format qui sera directement ingéré dans Elasticsearch en Phase 3 (un JSON = un document indexé).

## Après l'extraction : que faire du rapport (`extraction_log.csv`) ?

Trois colonnes à surveiller :

| Statut | Signification | Action |
|---|---|---|
| `ok` | Texte extrait normalement | Rien à faire |
| `ok_suspect_scan` | PDF probablement scanné (image), peu/pas de texte extrait | OCR nécessaire (voir ci-dessous) |
| `echec_telechargement` | Lien mort, inaccessible, ou non-PDF | Vérifier le lien dans le catalogue, chercher une source alternative (voir liste de portails discutée en Phase 1 : archives.sn, World Bank Documents, IRIS OMS) |
| `echec_extraction` | PDF corrompu / protégé par mot de passe | Ouvrir manuellement pour diagnostiquer |

## Pour les PDF scannés (OCR)

Certains documents anciens (1960-1990) seront probablement des scans sans couche de texte.
Étape suivante recommandée, à ajouter à ce même dossier une fois qu'on aura la liste des
`ok_suspect_scan` :

```bash
pip install pytesseract pdf2image
# + sudo apt install tesseract-ocr tesseract-ocr-fra poppler-utils
```

Je peux te fournir un second script `ocr_fallback.py` dès que tu as une première liste de
documents suspects scannés — pas besoin de l'écrire à l'aveugle maintenant.
