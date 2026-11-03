import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from google import genai
import time


# 1. Project directory
BASE_DIR = Path(__file__).resolve().parent

# 2. Knowledge-base document location
DOCUMENT_FILE = BASE_DIR / "knowledge_base" / "financial_guide.md"

# ChromaDB storage directory
CHROMA_DIR = BASE_DIR / "chroma_db"
# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# Retrieve Gemini API key securely
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# 3. Load the financial guide
def load_document():
    if not DOCUMENT_FILE.exists():
        raise FileNotFoundError(
            f"Knowledge-base document not found: {DOCUMENT_FILE}"
        )

    text = DOCUMENT_FILE.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError("The knowledge-base document is empty.")

    return text


# 4. Split the document into section-aware chunks
def split_into_chunks(text, chunk_size=1000):

    sections = text.split("\n## ")

    chunks = []

    for section in sections:

        section = section.strip()

        if not section:
            continue

        # Preserve the section heading
        if not section.startswith("#"):
            section = "## " + section

        # Keep smaller sections together
        if len(section) <= chunk_size:
            chunks.append(section)
            continue

        # Split longer sections into smaller chunks
        start = 0

        while start < len(section):

            end = start + chunk_size

            chunk = section[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start = end

    return chunks

# 5. Generate embeddings for document chunks
def generate_embeddings(chunks):
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        local_files_only=True
    )

    embeddings = model.encode(
        chunks,
        show_progress_bar=True
    )

    return embeddings

# 6. Store document chunks and embeddings in ChromaDB
def store_in_chromadb(chunks, embeddings):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_or_create_collection(
        name="spendsense_financial_guide",
        metadata={"description": "SpendSense financial literacy knowledge base"}
    )
    # Remove previous records before storing updated chunks
    existing_records = collection.get()

    if existing_records["ids"]:
        collection.delete(ids=existing_records["ids"])

    reference_map = {
            "1. Understanding Income and Expenses":
                "https://www.moneyhelper.org.uk/en/everyday-money/budgeting/beginners-guide-to-managing-your-money",
            "2. Creating a Personal Budget":
                "https://www.moneyhelper.org.uk/en/everyday-money/budgeting/beginners-guide-to-managing-your-money; https://www.moneyhelper.org.uk/en/everyday-money/budgeting/how-to-budget-for-an-irregular-income",
            "3. Building an Emergency Fund":
                "https://www.moneyhelper.org.uk/en/savings/types-of-savings/emergency-savings-how-much-is-enough",
            "4. Understanding Recurring Payments":
                "https://www.moneyhelper.org.uk/en/everyday-money/banking/direct-debits-and-standing-orders",
            "References":
                "https://www.moneyhelper.org.uk/en/everyday-money/budgeting/beginners-guide-to-managing-your-money; https://www.moneyhelper.org.uk/en/savings/types-of-savings/emergency-savings-how-much-is-enough; https://www.moneyhelper.org.uk/en/everyday-money/banking/direct-debits-and-standing-orders; https://www.moneyhelper.org.uk/en/everyday-money/budgeting/how-to-budget-for-an-irregular-income"
        }

    collection.upsert(
        ids=[f"financial_guide_{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "source": "financial_guide.md",
                "chunk_number": i,
                "section": chunk.splitlines()[0].lstrip("# ").strip(),
                "reference_urls": reference_map.get(
                    chunk.splitlines()[0].lstrip("# ").strip(),
                    ""
                )
            }
            for i, chunk in enumerate(chunks)
        ]
    )

    return collection

# 8. Search the knowledge base
def search_knowledge_base(query, collection, model, n_results=3):

    query_embedding = model.encode([query])

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=n_results
    )

    return results

# 10. Initialise Gemini client
def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found. Check your .env file."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    return client

# 11. Generate answers grounded in retrieved knowledge
def generate_grounded_answer(question, retrieved_chunks):

    client = get_gemini_client()

    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
You are SpendSense, a responsible personal finance assistant.

Answer the user's question using only the financial information
provided in the context below.

Instructions:
1. Do not invent financial facts or recommendations.
2. Do not use information outside the supplied context.
3. If the context does not contain enough information, say so.
4. Explain your answer clearly and simply.
5. Include the source document in your answer.
6. Do not calculate transaction totals or invent personal financial data.

Context:
{context}

User question:
{question}

Provide a clear, grounded answer.
"""

    # Retry Gemini request if the service is temporarily unavailable
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            return response.text

        except Exception as error:
            if attempt == 2:
                raise

            print(
                f"Gemini request failed. "
                f"Retrying in 5 seconds... ({attempt + 1}/3)"
            )

            time.sleep(5)



# 12. Run the complete RAG pipeline
if __name__ == "__main__":

    # Load the financial guide
    document = load_document()

    # Split into chunks
    chunks = split_into_chunks(document)
    print("\nTotal chunks created:", len(chunks))

    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i}:")
        print(chunk[:150])

    # Load the embedding model
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        local_files_only=True
    )

    # Generate embeddings
    embeddings = model.encode(chunks, show_progress_bar=True)

    # Store chunks in ChromaDB
    collection = store_in_chromadb(chunks, embeddings)

    # Verify stored metadata in ChromaDB
    stored_data = collection.get(include=["metadatas"])

    print("\nVERIFIED STORED METADATA:")

    for metadata in stored_data["metadatas"]:
        print(metadata)

    # Ask a financial-literacy question
    question = "How much money should I keep aside for emergencies?"

    # Retrieve relevant knowledge
    results = search_knowledge_base(
        question,
        collection,
        model,
        n_results=3
    )

    retrieved_chunks = results["documents"][0]

    # Generate a grounded answer
    answer = generate_grounded_answer(
        question,
        retrieved_chunks
    )

    print("\n" + "=" * 60)
    print("SPENDSENSE AI ASSISTANT")
    print("=" * 60)

    print(f"\nQuestion: {question}")

    print("\nGenerated Answer:")
    print(answer)

    print("\nSources:")
    for metadata in results["metadatas"][0]:
        print(
            f"- {metadata['source']}, "
            f"chunk {metadata['chunk_number']}"
        )