from pathlib import Path
from functools import lru_cache
import os
import time

import chromadb
from sentence_transformers import SentenceTransformer
from google import genai
from dotenv import load_dotenv

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ChromaDB storage directory
CHROMA_DIR = BASE_DIR / "chroma_db"

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model configuration
EMBEDDING_MODEL = str(BASE_DIR / "app" / "all-MiniLM-L6-v2")
GEMINI_MODEL = "gemini-3.5-flash-lite"

# ChromaDB collection name
COLLECTION_NAME = "spendsense_financial_guide"

@lru_cache(maxsize=1)
def get_rag_resources():
    """
    Load the embedding model, ChromaDB collection
    and Gemini client.
    """

    # Check that the Gemini API key exists
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    # Load the local embedding model
    model = SentenceTransformer(
        EMBEDDING_MODEL,
        local_files_only=True
    )

    # Connect to the existing ChromaDB database
    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    # Retrieve the existing financial guide collection
    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )

    # Create Gemini client
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    return model, collection, gemini_client

def retrieve_knowledge(question, collection, model, n_results=3):
    """
    Retrieve relevant financial knowledge from ChromaDB.
    """

    # Convert the user's question into an embedding
    question_embedding = model.encode([question])

    # Search the existing knowledge collection
    results = collection.query(
        query_embeddings=question_embedding.tolist(),
        n_results=n_results
    )

    return results

def generate_grounded_answer(question, retrieved_chunks, gemini_client):
    """
    Generate an answer using only the retrieved financial knowledge.
    """

    # Prepare the retrieved information as context
    context = "\n\n".join(retrieved_chunks)

    # Build the prompt
    prompt = f"""
    You are SpendSense, a responsible personal finance assistant.

    Answer the user's question using only the financial information
    provided in the context below.

    Instructions:
    - Use only the supplied context as evidence.
    - Do not invent financial facts or recommendations.
    - If the context does not contain enough information,
      clearly say so.
    - Explain financial concepts in simple language.
    - Do not calculate personal transaction amounts.
    - Include the source document in your answer.

    Context:
    {context}

    User Question:
    {question}

    Answer:
    """

    # Retry Gemini request up to three times
    for attempt in range(3):
        try:
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            return response.text

        except Exception:
            if attempt == 2:
                raise

            print(
                f"Gemini request failed. "
                f"Retrying in 5 seconds... ({attempt + 1}/3)"
            )

            time.sleep(5)

def ask_financial_question(question):
    """
    Complete RAG workflow for answering financial questions.
    """

    # Load the RAG resources
    model, collection, gemini_client = get_rag_resources()

    # Retrieve relevant knowledge
    results = retrieve_knowledge(
        question,
        collection,
        model
    )

    # Extract retrieved document chunks
    retrieved_chunks = results["documents"][0]

    # Generate an answer using Gemini
    answer = generate_grounded_answer(
        question,
        retrieved_chunks,
        gemini_client
    )

    # Extract source information
    sources = []

    for metadata in results["metadatas"][0]:
        sources.append({
            "document": metadata["source"],
            "section": metadata["section"],
            "chunk_number": metadata["chunk_number"],
            "reference_urls": metadata["reference_urls"]
        })

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }