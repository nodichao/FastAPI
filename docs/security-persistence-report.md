# Rapport de securite et de persistance

## Objet

Ce document decrit la persistance SQLite, le flux d'authentification JWT et la regle de propriete appliquee aux conversations et aux messages.

## Schema de base de donnees

La base est SQLite et son URL est configuree dans `app/database.py` :

```text
sqlite:///./app.db
```

Les tables sont creees au demarrage par `Base.metadata.create_all(bind=engine)`.
Cette operation cree les tables absentes, mais ne remplace pas un systeme de migrations pour les evolutions de schema.

### `users`

| Colonne | Role |
| --- | --- |
| `id` | Cle primaire texte, generee comme UUID |
| `username` | Nom unique et obligatoire |
| `email` | Adresse unique et obligatoire |
| `created_at` | Date de creation |
| `hashed_password` | Mot de passe hache, jamais le mot de passe en clair |

### `conversations`

| Colonne | Role |
| --- | --- |
| `id` | Cle primaire UUID |
| `user_id` | Identifiant du proprietaire |
| `created_at` | Date de creation |

`user_id` reference `users.id`. Une conversation appartient donc a un seul utilisateur.

### `messages`

| Colonne | Role |
| --- | --- |
| `id` | Cle primaire UUID |
| `conversation_id` | Conversation associee |
| `user_id` | Utilisateur qui a produit le message |
| `content` | Contenu du message |
| `role` | `user` ou `assistant` |
| `timestamp` | Date du message |

`conversation_id` reference `conversations.id` et `user_id` reference `users.id`.

## Flux d'authentification

1. Le client envoie son email et son mot de passe a `POST /auth`.
2. La route recherche l'utilisateur par email.
3. `verify_password` compare le mot de passe fourni au hash stocke.
4. En cas de succes, `create_access_token` produit un JWT signe avec `SECRET_KEY` et l'algorithme `HS256`.
5. L'identifiant utilisateur est place dans la claim `sub` du token.
6. Le client transmet ensuite le token dans chaque route protegee :

```http
Authorization: Bearer <access_token>
```

7. `get_current_user` recupere le token avec `HTTPBearer`, verifie la signature et l'expiration, lit `sub`, puis charge l'utilisateur avec `db.get(UserModel, user_id)`.
8. Si le token est invalide, expire, incomplet ou associe a un utilisateur inexistant, la requete est refusee avec `401`.

La `SECRET_KEY` doit etre longue, aleatoire et fournie par l'environnement ou le fichier `.env`. Un changement de cle invalide les tokens emis avec l'ancienne cle.

## Routes protegees

Les routes suivantes utilisent `Depends(get_current_user)` :

- `GET /me`
- `POST /conversations`
- `POST /messages`

La dependance injecte l'utilisateur authentifie dans `current_user`.

## Regle de propriete

Une conversation ne doit etre accessible qu'a son proprietaire. Dans `POST /messages`, la recherche est volontairement faite avec deux criteres :

```python
statement = select(ConversationModel).where(
    ConversationModel.id == message.conversation_id,
    ConversationModel.user_id == current_user.id,
)
```

Ainsi, connaitre l'identifiant d'une conversation ne suffit pas. Si la conversation existe mais appartient a un autre utilisateur, la requete ne renvoie aucun resultat et l'API retourne `404 Conversation not found`.

Lorsqu'une nouvelle conversation est creee, `user_id` est toujours initialise avec `current_user.id`. Les messages sont ensuite rattaches a cette conversation et a ce meme utilisateur.

Cette verification doit rester cote serveur. Il ne faut jamais faire confiance a un `user_id` fourni par le client pour autoriser l'acces a des donnees privees.

## Test de protection des donnees privees

Le test suivant verifie la condition d'autorisation au niveau de la persistance. Il cree une conversation pour un proprietaire, puis tente de la rechercher comme un autre utilisateur. Le resultat doit etre nul.

```python
import uuid

from sqlalchemy import select

from app.models import ConversationModel, UserModel


def test_user_cannot_access_another_users_conversation(db_session):
    owner = UserModel(
        id=str(uuid.uuid4()),
        username="owner",
        email="owner@example.com",
        hashed_password="test-hash",
    )
    other_user = UserModel(
        id=str(uuid.uuid4()),
        username="other",
        email="other@example.com",
        hashed_password="test-hash",
    )
    conversation = ConversationModel(
        id=str(uuid.uuid4()),
        user_id=owner.id,
    )

    db_session.add_all([owner, other_user, conversation])
    db_session.commit()

    statement = select(ConversationModel).where(
        ConversationModel.id == conversation.id,
        ConversationModel.user_id == other_user.id,
    )

    result = db_session.scalars(statement).first()

    assert result is None
```

Un test HTTP complementaire doit verifier que `POST /messages` retourne `404` lorsqu'un utilisateur authentifie fournit l'identifiant d'une conversation appartenant a quelqu'un d'autre. Ce test doit remplacer la dependance de base de donnees et `get_current_user`, afin de rester independant de la base locale et de l'API Groq.

## Points de vigilance

- Ne jamais commiter `.env` ni afficher `SECRET_KEY` ou `GROQ_API_KEY` dans les logs.
- Regenerer un token apres toute modification de `SECRET_KEY`.
- `create_all` ne migre pas les tables existantes ; utiliser Alembic pour les changements de schema.
- Les tests actuels du depot doivent etre alignes avec les routes effectivement exposees : le test de propriete ci-dessus couvre le controle de confidentialite qui n'etait pas present dans la suite initiale.
