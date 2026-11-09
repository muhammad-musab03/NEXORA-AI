
"""
WOLF AI - Professional RAG Engine
---------------------------------
Features:
- PDF, TXT, MD and DOCX support
- Persistent ChromaDB vector database
- Local HuggingFace embeddings
- Semantic document search
- Smart overlapping text chunking
- Duplicate document detection
- Document listing and deletion
- Source and page citations
- Metadata filtering
- Persistent storage after app restart
- Error handling and validation
"""

import hashlib
import logging
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from io import BytesIO

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_DIR = BASE_DIR / "vector_db"
DOCUMENTS_DIR = BASE_DIR / "documents"

COLLECTION_NAME = "wolf_ai_documents"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 200
CHUNK_OVERLAP = 40

TOP_K = 5
MIN_SCORE = 0.25

MAX_FILE_SIZE = 25 * 1024 * 1024

SUPPORTED_FORMATS = {
    ".pdf",
    ".txt",
    ".md",
    ".docx"
}

BATCH_SIZE = 100

# Create required directories
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WOLF_RAG")


# ==========================================
# STEP 1: LOAD EMBEDDING MODEL
# ==========================================

@lru_cache(maxsize=1)
def load_embedding_model():
    """
    Load the local embedding model once.
    The model converts text into numerical vectors.
    """

    logger.info("Loading WOLF AI embedding model...")

    model = SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )

    logger.info("Embedding model loaded successfully.")

    return model


# ==========================================
# STEP 2: DOCUMENT UTILITIES
# ==========================================

def calculate_file_hash(file_bytes):
    """Generate SHA256 hash for duplicate detection."""

    return hashlib.sha256(file_bytes).hexdigest()


def validate_document(filename, file_bytes):
    """Validate uploaded document."""

    if not filename:
        raise ValueError("Document filename is missing.")

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format: {extension}. "
            "Supported formats: PDF, TXT, MD and DOCX."
        )

    if not file_bytes:
        raise ValueError("Uploaded document is empty.")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError("File size exceeds the 25 MB limit.")

    return extension


# ==========================================
# STEP 3: DOCUMENT TEXT EXTRACTION
# ==========================================

def read_pdf_pages(file_bytes):
    """Extract text from every PDF page."""

    reader = PdfReader(BytesIO(file_bytes))

    if reader.is_encrypted:
        if not reader.decrypt(""):
            raise ValueError(
                "Password-protected PDF cannot be opened."
            )

    pages = []

    for number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "page": number,
                "text": text.strip()
            })

    if not pages:
        raise ValueError(
            "No readable text found in PDF. "
            "Scanned PDFs require OCR processing."
        )

    return pages


def read_text_file(file_bytes):
    """Read TXT and Markdown documents."""

    try:
        text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1")

    if not text.strip():
        raise ValueError("Document contains no readable text.")

    return [{
        "page": 1,
        "text": text.strip()
    }]


def read_docx_file(file_bytes):
    """Extract text from Word documents."""

    from docx import Document

    document = Document(BytesIO(file_bytes))

    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    text = "\n".join(paragraphs)

    if not text:
        raise ValueError("No readable text found in DOCX.")

    return [{
        "page": 1,
        "text": text
    }]


def read_document(filename, file_bytes):
    """Automatically select the correct document reader."""

    extension = validate_document(filename, file_bytes)

    if extension == ".pdf":
        return read_pdf_pages(file_bytes)

    if extension in {".txt", ".md"}:
        return read_text_file(file_bytes)

    if extension == ".docx":
        return read_docx_file(file_bytes)

    raise ValueError("Unsupported document format.")


# ==========================================
# STEP 4: SMART TEXT CHUNKING
# ==========================================

def split_into_chunks(
    pages,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):
    """
    Divide document text into smaller overlapping chunks.
    Page information is preserved for citations.
    """

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk overlap.")

    step = chunk_size - overlap

    chunks = []

    for page in pages:

        words = page["text"].split()

        start = 0

        while start < len(words):

            chunk_words = words[
                start:start + chunk_size
            ]

            chunk_text = " ".join(chunk_words)

            if chunk_text.strip():

                chunks.append({
                    "text": chunk_text,
                    "page": int(page["page"])
                })

            if start + chunk_size >= len(words):
                break

            start += step

    if not chunks:
        raise ValueError("No text chunks could be generated.")

    return chunks


# ==========================================
# STEP 5: GENERATE EMBEDDINGS
# ==========================================

def embed_texts(texts):
    """
    Convert text into normalized numerical vectors.
    """

    if not texts:
        return []

    model = load_embedding_model()

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    return vectors.tolist()


# ==========================================
# STEP 6: PERSISTENT VECTOR DATABASE
# ==========================================

class RAGStore:
    """
    WOLF AI persistent document intelligence system.

    Documents and their embeddings remain saved
    even after the application is closed.
    """

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=str(DATABASE_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "description": "WOLF AI document knowledge base",
                "hnsw:space": "cosine"
            }
        )

        logger.info(
            "WOLF AI vector database initialized."
        )

    # --------------------------------------
    # ADD DOCUMENT
    # --------------------------------------

    def add_document(self, filename, file_bytes):
        """Extract, process and permanently store a document."""

        extension = validate_document(filename, file_bytes)

        file_hash = calculate_file_hash(file_bytes)

        # Check whether identical content already exists.
        existing = self.collection.get(
            where={"file_hash": file_hash},
            limit=1
        )

        if existing["ids"]:
            raise ValueError(
                "This document has already been uploaded."
            )

        # Extract document text.
        pages = read_document(filename, file_bytes)

        # Split into chunks.
        chunks = split_into_chunks(pages)

        texts = [chunk["text"] for chunk in chunks]

        # Generate vectors.
        embeddings = embed_texts(texts)

        uploaded_at = datetime.now(
            timezone.utc
        ).isoformat()

        ids = []
        metadatas = []
        documents = []

        for index, chunk in enumerate(chunks):

            chunk_id = hashlib.sha256(
                f"{file_hash}:{index}".encode()
            ).hexdigest()

            ids.append(chunk_id)

            documents.append(chunk["text"])

            metadatas.append({
                "source": filename,
                "file_hash": file_hash,
                "file_type": extension,
                "page": int(chunk["page"]),
                "chunk_index": index,
                "uploaded_at": uploaded_at
            })

        # Store in batches.
        for start in range(0, len(ids), BATCH_SIZE):

            end = start + BATCH_SIZE

            self.collection.add(
                ids=ids[start:end],
                documents=documents[start:end],
                embeddings=embeddings[start:end],
                metadatas=metadatas[start:end]
            )

        logger.info(
            "Document added: %s (%s chunks)",
            filename,
            len(chunks)
        )

        return {
            "filename": filename,
            "chunks": len(chunks),
            "pages": len(pages),
            "file_hash": file_hash,
            "status": "success"
        }

    # Backward-compatible PDF method.
    def add_pdf(self, filename, file_bytes):
        return self.add_document(filename, file_bytes)

    # --------------------------------------
    # SEARCH DOCUMENTS
    # --------------------------------------

    def search(
        self,
        question,
        top_k=TOP_K,
        min_score=MIN_SCORE,
        source=None
    ):
        """
        Search for relevant document chunks.

        Results are sorted by semantic similarity.
        """

        if not question or not question.strip():
            return []

        if top_k <= 0:
            return []

        if self.collection.count() == 0:
            return []

        question_vector = embed_texts([
            question.strip()
        ])[0]

        search_args = {
            "query_embeddings": [question_vector],
            "n_results": min(
                top_k,
                self.collection.count()
            ),
            "include": [
                "documents",
                "metadatas",
                "distances"
            ]
        }

        if source:
            search_args["where"] = {
                "source": source
            }

        results = self.collection.query(
            **search_args
        )

        matches = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            # Cosine similarity = 1 - cosine distance.
            score = 1.0 - float(distance)

            if score < min_score:
                continue

            matches.append({
                "text": document,
                "source": metadata["source"],
                "page": metadata["page"],
                "score": score,
                "chunk_index": metadata["chunk_index"]
            })

        return matches

    # --------------------------------------
    # LIST DOCUMENTS
    # --------------------------------------

    def list_documents(self):
        """Return unique uploaded documents and their details."""

        total = self.collection.count()

        if total == 0:
            return []

        data = self.collection.get(
            include=["metadatas"],
            limit=total
        )

        documents = {}

        for metadata in data["metadatas"]:

            file_hash = metadata["file_hash"]

            if file_hash not in documents:

                documents[file_hash] = {
                    "filename": metadata["source"],
                    "file_type": metadata["file_type"],
                    "uploaded_at": metadata["uploaded_at"],
                    "chunks": 0
                }

            documents[file_hash]["chunks"] += 1

        return list(documents.values())

    # --------------------------------------
    # DELETE DOCUMENT
    # --------------------------------------

    def delete_document(self, filename):
        """Delete a document and all its stored chunks."""

        existing = self.collection.get(
            where={"source": filename},
            include=["metadatas"]
        )

        if not existing["ids"]:
            return False

        self.collection.delete(
            ids=existing["ids"]
        )

        logger.info("Document deleted: %s", filename)

        return True

    # --------------------------------------
    # CLEAR KNOWLEDGE BASE
    # --------------------------------------

    def clear(self):
        """Delete all documents from the vector database."""

        self.client.delete_collection(
            name=COLLECTION_NAME
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "description": "WOLF AI document knowledge base",
                "hnsw:space": "cosine"
            }
        )

        logger.warning("WOLF AI knowledge base cleared.")

    # --------------------------------------
    # DATABASE STATISTICS
    # --------------------------------------

    def get_stats(self):
        """Return knowledge base statistics."""

        documents = self.list_documents()

        return {
            "total_documents": len(documents),
            "total_chunks": self.collection.count(),
            "database_path": str(DATABASE_DIR),
            "embedding_model": EMBEDDING_MODEL_NAME
        }


# ==========================================
# STEP 7: BUILD AI CONTEXT
# ==========================================

def build_context(results):
    """
    Prepare retrieved information for Groq AI.

    Includes source names and page numbers.
    """

    if not results:
        return ""

    context_parts = []

    for index, result in enumerate(results, start=1):

        context_parts.append(
            f"""
[Source {index}]

Document: {result['source']}
Page: {result['page']}
Relevance: {result['score']:.3f}

Content:
{result['text']}
"""
        )

    return "\n\n--------------------\n\n".join(
        context_parts
    )


# ==========================================
# STEP 8: SOURCE CITATIONS
# ==========================================

def get_sources(results):
    """Return unique source and page references."""

    sources = []

    seen = set()

    for result in results:

        reference = (
            result["source"],
            result["page"]
        )

        if reference not in seen:

            seen.add(reference)

            sources.append({
                "filename": result["source"],
                "page": result["page"],
                "score": result["score"]
            })

    return sources


# ==========================================
# STEP 9: QUICK DATABASE TEST
# ==========================================

if __name__ == "__main__":

    print("\nWOLF AI RAG ENGINE")
    print("========================")

    store = RAGStore()

    stats = store.get_stats()

    print("\nDatabase Statistics:")

    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\nSaved Documents:")

    documents = store.list_documents()

    if documents:

        for document in documents:
            print(
                f"- {document['filename']} "
                f"({document['chunks']} chunks)"
            )

    else:
        print("No documents uploaded yet.")

    print("\nWOLF AI RAG Engine is ready.")
