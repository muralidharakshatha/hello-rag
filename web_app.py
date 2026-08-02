"""A small Flask website for chatting with the Lumen Bikes RAG app."""

# Flask serves the web page and receives questions from the browser.
from flask import Flask, jsonify, render_template, request

# Import the shared RAG function from the terminal application.
from app import answer_question

# Create the Flask application.
web_app = Flask(__name__)


# Show the chatbot page when someone visits the home URL.
@web_app.get("/")
def home():
    """Render the chatbot interface."""

    return render_template("index.html")


# Receive a question, run RAG, and return JSON to the browser.
@web_app.post("/api/chat")
def chat():
    """Answer one browser-submitted question."""

    # Read the JSON body safely and remove extra spaces from the question.
    question = request.get_json(silent=True) or {}
    question_text = str(question.get("question", "")).strip()

    # Reject empty questions with a helpful message.
    if not question_text:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        # Use the same PostgreSQL-backed RAG function as the terminal app.
        retrieved_fact, answer = answer_question(question_text)
    except Exception:
        # Keep secrets and technical details out of browser error messages.
        return jsonify({"error": "I could not answer that. Please try again."}), 500

    # Return the answer and source fact for display in the chat.
    return jsonify({"answer": answer, "fact": retrieved_fact})


# Start the local development server when this file is run directly.
if __name__ == "__main__":
    web_app.run(host="127.0.0.1", port=5000, debug=False)
