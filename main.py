from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


feedbacks: list[dict] = [
    {
        "id": 1,
        "username": "Madame Morrible",
        "rating": 10,
        "feedback": "Absolutely stunning!"
    },
    {
        "id": 2,
        "username": "Glindaaaa",
        "rating": 10,
        "feedback": "You're gonna be popular but not as popular as me."
    },
    {
        "id": 3,
        "username": "Elphaba",
        "rating": 9,
        "feedback": "Acceptable but needs more green."
    }
]


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/feedbacks", response_class=HTMLResponse, include_in_schema=False)
def home():
    return f"<h1>{feedbacks[0]['feedback']}</h1>"


@app.get("/api/feedbacks")
def get_feedbacks():
    return feedbacks


@app.get("/api/feedbacks/{feedback_id}")
def get_feedback(feedback_id: int):
    for feedback in feedbacks:
        if feedback.get("id") == feedback_id:
            return feedback
    return {"detail": "Feedback not found."}
