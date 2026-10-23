# from fastapi import FastAPI
# from pydantic import BaseModel, Field
# import datetime


# class QuizModel(BaseModel):
#     topic: str = Field(min_length=2, max_length=100)
#     nbQuestions: int = Field(ge=1, le=20)


# class SummaryModel(BaseModel):
#     text: str = Field(min_length=10, max_length=5000)
#     max_bullets: int = Field(ge=1, le=10)


# class ChatModel(BaseModel):
#     message: str = Field(min_length=1, max_length=1000)


# app = FastAPI()


# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy",
#         "version": "1.0.0",
#         "timestamp": datetime.datetime.now().isoformat()
#     }


# @app.post("/chat")
# def chat(message: ChatModel):
#     return {
#         "answer": "Welcome to the chat endpoint!"
#     }


# @app.post("/quiz")
# def quiz(quiz: QuizModel):
#     questions = [
#         f"Question {i} about {quiz.topic}"
#         for i in range(1, quiz.nbQuestions + 1)
#     ]

#     return {
#         "questions": questions
#     }


# @app.post("/summarise")
# def summarise(summary: SummaryModel):
#     return {
#         "summary": f"Summary created with max {summary.max_bullets} bullets."
#     }



from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="API Conversations",
    version="1.0.0"
)

app.include_router(router)
