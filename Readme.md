# FastAPI Backend — API d'assistance

Backend REST développé avec **FastAPI** dans le cadre d'un exercice d'intégration d'API.

L'objectif est de construire une API simple permettant de :

* vérifier l'état du serveur ;
* envoyer un message à une API de chat ;
* générer un quiz à partir d'un thème ;
* générer un résumé à partir d'un texte.

> Les fonctionnalités d'IA sont volontairement simulées dans cette première version. L'objectif du checkpoint est principalement de mettre en place la structure de l'API, la validation des données et les tests.

## Technologies utilisées

* Python
* FastAPI
* Pydantic
* Uvicorn
* Pytest
* HTTPX / TestClient

## Structure du projet

```text
FastAPI/
├── main.py
├── tests/
│   └── test_api.py
├── docs/
│   └── api-test-report.md
├── requirements.txt
└── README.md
```

## Installation

### 1. Cloner le projet

```bash
git clone <URL_DU_PROJET>
cd FastAPI
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
```

### 3. Activer l'environnement virtuel

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

## Lancer l'API

Depuis le dossier du projet :

```bash
fastapi dev main.py
```

L'API sera disponible à l'adresse :

```text
http://127.0.0.1:8000
```

Il est également possible d'utiliser Uvicorn directement :

```bash
uvicorn main:app --reload
```

## Documentation de l'API

FastAPI génère automatiquement une documentation interactive.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

Swagger UI permet notamment de tester directement les différentes routes.

# Endpoints

## 1. Health Check

### `GET /health`

Permet de vérifier que l'API fonctionne.

Cette route ne fait appel à aucun modèle d'IA.

### Exemple de réponse

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-09-15T18:30:00"
}
```

## 2. Chat

### `POST /chat`

Reçoit un message utilisateur et retourne une réponse structurée.

### Requête

```json
{
  "message": "Bonjour"
}
```

### Réponse

```json
{
  "answer": "Welcome to the chat endpoint!"
}
```

### Validation

Le champ `message` :

* est obligatoire ;
* doit contenir au moins 1 caractère ;
* peut contenir au maximum 1000 caractères.

Une requête invalide retourne une erreur HTTP `422`.

## 3. Quiz

### `POST /quiz`

Permet de générer une liste de questions à partir d'un thème.

### Requête

```json
{
  "topic": "Python",
  "nbQuestions": 3
}
```

### Réponse

```json
{
  "questions": [
    "Question 1 about Python",
    "Question 2 about Python",
    "Question 3 about Python"
  ]
}
```

### Validation

Le champ `topic` :

* doit contenir entre 2 et 100 caractères.

Le champ `nbQuestions` :

* doit être supérieur ou égal à `1` ;
* doit être inférieur ou égal à `20`.

## 4. Summarise

### `POST /summarise`

Permet de générer un résumé à partir d'un texte.

### Requête

```json
{
  "text": "FastAPI est un framework Python permettant de créer des APIs modernes.",
  "max_bullets": 3
}
```

### Réponse

```json
{
  "summary": "Summary created with max 3 bullets."
}
```

### Validation

Le champ `text` :

* doit contenir entre 10 et 5000 caractères.

Le champ `max_bullets` :

* doit être supérieur ou égal à `1` ;
* doit être inférieur ou égal à `10`.

# Validation des données

La validation des données est réalisée avec **Pydantic**.

Exemple :

```python
class ChatModel(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
```

Cela permet à FastAPI de vérifier automatiquement les données reçues avant l'exécution de la logique de l'endpoint.

En cas de données invalides, l'API retourne une réponse HTTP :

```text
422 Unprocessable Entity
```

# Tests

Le projet contient des tests automatisés avec **pytest** et `TestClient`.

Pour lancer les tests :

```bash
python -m pytest
```

Les tests vérifient notamment :

* le fonctionnement de `GET /health` ;
* le fonctionnement de `POST /chat` ;
* les codes HTTP retournés ;
* la structure des réponses.

### Exemple de résultat

```text
collected 2 items

tests/test_api.py ..    [100%]

2 passed
```

# Tests manuels

Des tests ont également été réalisés avec **Swagger UI**.

Les tests comprennent notamment :

### Test valide

```json
{
  "message": "Bonjour"
}
```

Résultat attendu :

```text
200 OK
```

### Test invalide

```json
{
  "message": ""
}
```

Résultat attendu :

```text
422 Unprocessable Entity
```

Un rapport détaillé des tests est disponible dans :

```text
docs/api-test-report.md
```

# Objectifs du projet

Ce projet permet de mettre en pratique :

* la création d'une API avec FastAPI ;
* la définition de routes HTTP ;
* la création de modèles Pydantic ;
* la validation automatique des données ;
* la génération automatique de documentation OpenAPI ;
* l'utilisation de Swagger UI ;
* les tests automatisés avec pytest ;
* la simulation de requêtes HTTP avec TestClient ;
* la structuration d'un petit backend Python.

# Évolutions possibles

Dans une version ultérieure, les réponses simulées pourront être remplacées par de véritables fonctionnalités d'IA :

* intégration d'un LLM pour `/chat` ;
* génération réelle de quiz ;
* résumé automatique de textes ;
* gestion de l'historique conversationnel ;
* authentification des utilisateurs ;
* stockage des données dans une base de données ;
* gestion des erreurs et des logs de manière plus avancée.

## Auteur

Projet réalisé dans le cadre d'un exercice d'apprentissage de **FastAPI, Pydantic et des APIs REST**.
