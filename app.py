"""A tiny, beginner-friendly Retrieval-Augmented Generation (RAG) app."""

# os lets us read configuration values from environment variables.
import os

# Load values such as OPENAI_API_KEY from a local .env file, if one exists.
from dotenv import load_dotenv

# Document gives each company fact the format expected by LangChain.
from langchain_core.documents import Document

# ChatPromptTemplate helps us clearly tell the model how to answer.
from langchain_core.prompts import ChatPromptTemplate

# InMemoryVectorStore keeps embeddings in memory, with no database required.
from langchain_core.vectorstores import InMemoryVectorStore

# These classes connect LangChain to OpenAI's embedding and chat models.
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Psycopg lets Python read our company facts from PostgreSQL.
import psycopg


# Read environment variables from .env before creating the OpenAI clients.
load_dotenv()

# Read the database address, or use our local hello_rag database by default.
database_url = os.getenv("DATABASE_URL", "postgresql:///hello_rag")

# Open PostgreSQL, read every stored fact, and then close the connection.
with psycopg.connect(database_url) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT fact FROM company_facts ORDER BY id")
        rows = cursor.fetchall()

# Turn each database row into a LangChain Document.
facts = [Document(page_content=row[0]) for row in rows]

# Create an embedding model that turns text into lists of numbers.
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create an in-memory vector store and add the company facts to it.
vector_store = InMemoryVectorStore(embedding=embeddings)
vector_store.add_documents(facts)

# Build a prompt that requires the model to answer only from the retrieved fact.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer using only the provided fact. "
            "If the fact does not contain the answer, say you do not know.",
        ),
        ("human", "Fact: {fact}\n\nQuestion: {question}"),
    ]
)

# Create the language model that will write the final answer.
model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)


# Put the complete RAG process in a function that both interfaces can reuse.
def answer_question(question: str) -> tuple[str, str]:
    """Retrieve one fact and answer the question using only that fact."""

    # Find only the single fact whose meaning is most similar to the question.
    retrieved_fact = vector_store.similarity_search(question, k=1)[0].page_content

    # Fill in the prompt, call OpenAI, and get the text response.
    answer = (prompt | model).invoke({"fact": retrieved_fact, "question": question})

    # Return both values so the terminal or website can display them.
    return retrieved_fact, str(answer.content)


# Run this terminal interface only when app.py is launched directly.
if __name__ == "__main__":
    # Ask the user what they want to know about the fictional company.
    terminal_question = input("Ask a question about Lumen Bikes: ")

    # Run the shared RAG function for the terminal question.
    terminal_fact, terminal_answer = answer_question(terminal_question)

    # Show both what was retrieved and the final answer in the terminal.
    print(f"\nRetrieved fact: {terminal_fact}")
    print(f"Answer: {terminal_answer}")
