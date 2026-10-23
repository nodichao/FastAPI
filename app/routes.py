from fastapi import APIRouter, Depends, HTTPException,status
import datetime 
import os

from groq import Groq
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.dependencies import get_current_user
from app.models import UserModel, ConversationModel, MessageModel
from sqlalchemy.orm import Session
from app.schemas import User, Conversation, Message, LoginRequest
from app.security import create_access_token, hash_password, verify_password
from app.database import get_db 
router = APIRouter()


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@router.get("/me")
def get_me(
    current_user: UserModel = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email
    }

@router.get("/db_check")
def check_database(db: Session = Depends(get_db)):
    print(f"Database session: {db}")  # Affiche la session de base de données pour le débogage
    # Effectuer ici une petite requête SQLAlchemy
    return {"message": "Session de base de données disponible","Session": str(db)}

@router.post("/users")
def create_user(user: User, db: Session = Depends(get_db)):
    # Logic to create a user in the database
     # 1. Hasher le mot de passe
    print("process started")
    hashed_password = hash_password(user.password)

    # 2. Créer l'objet SQLAlchemy
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    try:
        # 3. Ajouter l'objet à la session
        db.add(db_user)

        # 4. Enregistrer les modifications
        db.commit()

        # 5. Actualiser l'objet pour récupérer son ID
        db.refresh(db_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cet email est déjà utilisé."
        )

    # 6. Renvoyer uniquement les données autorisées
    return {
        "message": "User created successfully",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "username": db_user.username,
            "created_at": db_user.created_at.isoformat()
        }
    }


@router.post("/conversations")
def create_conversation(conversation: Conversation, db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    # Logic to create a conversation in the database
    db_conversation = ConversationModel(
        user_id=current_user.id,
        created_at=datetime.datetime.now()

    )
    try:
            # 3. Ajouter l'objet à la session
            db.add(db_conversation)
    
            # 4. Enregistrer les modifications
            db.commit()
    
            # 5. Actualiser l'objet pour récupérer son ID
            db.refresh(db_conversation)


            
    
    except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Cet email est déjà utilisé."
            )
    
    # 6. Renvoyer uniquement les données autorisées
    return {
            "message": "Conversation created successfully",
            "conversation": {
                "id": db_conversation.id,
                "user_id": db_conversation.user_id,
                "created_at": db_conversation.created_at.isoformat()
            }
        }
    

@router.post("/messages")
def create_message(
    message: Message,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 1. Récupérer ou créer la conversation
    if message.conversation_id is not None:
        statement = select(ConversationModel).where(
            ConversationModel.id == message.conversation_id,
            ConversationModel.user_id == current_user.id
        )

        conversation = db.scalars(statement).first()

        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        conversation = ConversationModel(
            user_id=current_user.id,
            created_at=datetime.datetime.now()
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    try:
        # 2. Enregistrer le nouveau message utilisateur
        db_message = MessageModel(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role="user",
            content=message.content,
            timestamp=datetime.datetime.now()
        )

        db.add(db_message)
        db.commit()
        db.refresh(db_message)

        # 3. Récupérer tous les messages de cette conversation,
        # y compris le message utilisateur qui vient d'être enregistré
        messages_history = (
            db.query(MessageModel)
            .filter_by(conversation_id=conversation.id)
            .order_by(
                MessageModel.timestamp.asc(),
                MessageModel.id.asc()
            )
            .all()
        )

        # 4. Construire le contexte en conservant les rôles
        messages_to_send = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages_history
        ]

        # 5. Envoyer l'historique complet à Groq
        # Ne pas ajouter message.content une seconde fois :
        # il est déjà présent dans messages_to_send.
        chat_completion = client.chat.completions.create(
            messages=messages_to_send,
            model="openai/gpt-oss-20b",
        )

        # 6. Enregistrer la réponse de l'assistant
        assistant_message = MessageModel(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role="assistant",
            content=chat_completion.choices[0].message.content,
            timestamp=datetime.datetime.now()
        )

        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erreur d'intégrité lors de l'enregistrement du message."
        )

    # 7. Retourner la réponse
    return {
        "status_code": 200,
        "user_message": {
            "id": db_message.id,
            "conversation_id": db_message.conversation_id,
            "role": db_message.role,
            "content": db_message.content,
            "timestamp": db_message.timestamp.isoformat()
        },
        "assistant_message": {
            "id": assistant_message.id,
            "conversation_id": assistant_message.conversation_id,
            "role": assistant_message.role,
            "content": assistant_message.content,
            "timestamp": assistant_message.timestamp.isoformat()
        }
    }

     

@router.post("/auth")
def auth_check(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Check if a user is authenticated."""
    statemet = select(UserModel).where(UserModel.email == credentials.email)
    user = db.scalars(statemet).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    check_password = verify_password(credentials.password, user.hashed_password)
    if not check_password:
        raise HTTPException(status_code=401, detail="Invalid password")

    # Create an access token
    access_token = create_access_token(user.id)

    # If we reach here, the user is authenticated

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }