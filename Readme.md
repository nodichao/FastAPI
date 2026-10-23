# FastAPI Conversations API

Backend REST developpe avec FastAPI. L'API gere des utilisateurs, des conversations et des messages persistants dans SQLite. Les reponses de l'assistant sont generees par Groq.

## Technologies

- Python
- FastAPI et Pydantic
- SQLAlchemy avec SQLite
- JWT pour l'authentification
- pwdlib pour le hashage des mots de passe
- Groq pour les reponses de l'assistant
- Pytest et TestClient

## Structure

```text
FastAPI/
├── app/
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── schemas.py
│   └── security.py
├── docs/
│   ├── api-test-report.md
│   └── security-persistence-report.md
├── tests/
│   └── test_api.py
├── .env
├── requirements.txt
└── Readme.md
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Configurez ensuite `.env` :

```env
SECRET_KEY=une-cle-secrete-aleatoire-d-au-moins-32-octets
GROQ_API_KEY=votre-cle-groq
```

Ne commitez jamais `.env`. La base SQLite locale est creee dans `app.db` au demarrage. Les tables sont initialisees par SQLAlchemy si elles n'existent pas.

## Lancer l'API

Depuis la racine du projet :

```powershell
uvicorn app.main:app --reload
```

L'API est disponible sur `http://127.0.0.1:8000`.

Documentation interactive :

- Swagger UI : `http://127.0.0.1:8000/docs`
- ReDoc : `http://127.0.0.1:8000/redoc`

## Endpoints

### Verification

`GET /health` retourne :

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Utilisateurs

`POST /users` cree un compte. Exemple :

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "mot-de-passe-securise"
}
```

Le mot de passe brut n'est jamais stocke ; seul son hash est persiste.

### Authentification

`POST /auth` verifie l'email et le mot de passe et retourne un JWT :

```json
{
  "email": "alice@example.com",
  "password": "mot-de-passe-securise"
}
```

Pour les routes protegees, envoyez le token dans l'en-tete :

```http
Authorization: Bearer <access_token>
```

`GET /me` retourne l'utilisateur authentifie.

### Conversations

`POST /conversations` demarre une conversation pour l'utilisateur authentifie.

`POST /messages` ajoute un message et genere une reponse assistant. Corps minimal :

```json
{
  "conversation_id": "uuid-de-la-conversation",
  "content": "Bonjour"
}
```

Si `conversation_id` est omis, une nouvelle conversation est creee. Le message utilisateur et la reponse assistant sont tous deux enregistres dans `messages`.

Le serveur verifie que la conversation appartient a l'utilisateur authentifie avant d'y ajouter un message. Une conversation appartenant a un autre utilisateur est refusee.

## Persistance et securite

Les tables `users`, `conversations` et `messages` sont definies dans `app/models.py`. Les identifiants sont des UUID et les conversations/messages sont rattaches a leur proprietaire par `user_id`.

Le flux d'authentification est le suivant :

1. L'utilisateur s'inscrit avec `POST /users`.
2. Le mot de passe est hache avec `pwdlib`.
3. L'utilisateur se connecte avec `POST /auth`.
4. L'API emet un JWT contenant l'identifiant utilisateur dans `sub`.
5. `get_current_user` verifie le token et charge l'utilisateur.
6. Les routes protegees appliquent la regle de propriete.

Voir [docs/security-persistence-report.md](docs/security-persistence-report.md) pour le schema detaille et le test de protection des donnees privees.

## Tests

Lancer les tests avec :

```powershell
python -m pytest -q
```

Les tests utilisent `TestClient` et verifient notamment le health check et le refus d'une route protegee sans authentification.

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
