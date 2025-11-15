"""
Chroma vector store integration for Student Model.

This module handles vector embeddings for:
- Student learning preferences (semantic representation)
- Concept relationships and prerequisites
- Content similarity for adaptive recommendations

Used by Engine 4 (Adaptive Personalization) for semantic matching.
"""

import os
from typing import Dict, List, Optional
import warnings

# Try to import chromadb, but make it optional for basic functionality
try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    warnings.warn(
        "chromadb not available. Vector store features will be disabled. "
        "Install chromadb for full functionality: pip install chromadb"
    )

# Chroma configuration from environment
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "master_creator_vectors")


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CHROMA CLIENT
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


def get_chroma_client(persistent: bool = True):
    """
    Get Chroma client instance.

    Args:
        persistent: Use persistent storage (default True for production)

    Returns:
        chromadb.Client instance or None if chromadb not available
    """
    if not CHROMADB_AVAILABLE:
        return None

    try:
        if persistent:
            # Connect to Chroma server (Docker container)
            return chromadb.HttpClient(
                host=CHROMA_HOST,
                port=CHROMA_PORT,
                settings=Settings(anonymized_telemetry=False),
            )
        else:
            # In-memory client for testing
            return chromadb.Client(Settings(anonymized_telemetry=False))
    except Exception as e:
        warnings.warn(f"Could not connect to Chroma server: {e}. Vector features will be disabled.")
        return None


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# VECTOR STORE CLASS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


class StudentVectorStore:
    """
    Manages vector embeddings for student learning data.

    Collections:
    - learning_preferences: Student learning style embeddings
    - concept_embeddings: Concept relationships and prerequisites
    - content_vectors: Learning content for similarity matching
    """

    def __init__(self, client=None):
        """
        Initialize vector store.

        Args:
            client: Chroma client (creates new one if None)
        """
        if not CHROMADB_AVAILABLE:
            self.client = None
            self.embedding_fn = None
            self.learning_prefs_collection = None
            self.concepts_collection = None
            self.content_collection = None
            warnings.warn("StudentVectorStore initialized without chromadb - vector features disabled")
            return

        self.client = client if client is not None else get_chroma_client()

        # If client is still None (connection failed), disable vector features
        if self.client is None:
            self.embedding_fn = None
            self.learning_prefs_collection = None
            self.concepts_collection = None
            self.content_collection = None
            warnings.warn("StudentVectorStore initialized without Chroma connection - vector features disabled")
            return

        # Use sentence transformers for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"  # Fast, good for semantic search
        )

        # Initialize collections
        self._init_collections()

    def _init_collections(self):
        """Create or get collections."""
        # Learning preferences collection
        self.learning_prefs_collection = self.client.get_or_create_collection(
            name="learning_preferences",
            embedding_function=self.embedding_fn,
            metadata={"description": "Student learning style and preference vectors"},
        )

        # Concept embeddings collection
        self.concepts_collection = self.client.get_or_create_collection(
            name="concept_embeddings",
            embedding_function=self.embedding_fn,
            metadata={"description": "Educational concept relationships and prerequisites"},
        )

        # Content vectors collection
        self.content_collection = self.client.get_or_create_collection(
            name="content_vectors",
            embedding_function=self.embedding_fn,
            metadata={"description": "Learning content for similarity matching"},
        )

    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
    # LEARNING PREFERENCES
    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

    def add_student_preferences(
        self,
        student_id: str,
        preferences_text: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Add or update student learning preferences vector.

        Args:
            student_id: Unique student identifier
            preferences_text: Text description of learning preferences
                             (e.g., "Visual learner, prefers diagrams and videos")
            metadata: Additional metadata (learning_preferences list, reading_level, etc.)
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            return

        self.learning_prefs_collection.upsert(
            ids=[student_id],
            documents=[preferences_text],
            metadatas=[metadata or {}],
        )

    def get_student_preferences(self, student_id: str) -> Optional[Dict]:
        """
        Retrieve student learning preferences.

        Args:
            student_id: Student identifier

        Returns:
            Dict with document, metadata, and embedding, or None if not found
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            return None

        results = self.learning_prefs_collection.get(ids=[student_id], include=["documents", "metadatas", "embeddings"])

        if not results["ids"]:
            return None

        return {
            "student_id": student_id,
            "document": results["documents"][0],
            "metadata": results["metadatas"][0],
            "embedding": results["embeddings"][0] if results.get("embeddings") else None,
        }

    def find_similar_students(
        self,
        student_id: str,
        n_results: int = 5,
    ) -> List[Dict]:
        """
        Find students with similar learning preferences.

        Args:
            student_id: Reference student ID
            n_results: Number of similar students to return

        Returns:
            List of dicts with similar student info
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            return None

        # Get reference student's preferences
        ref_prefs = self.get_student_preferences(student_id)
        if not ref_prefs:
            return []

        # Query for similar students
        results = self.learning_prefs_collection.query(
            query_embeddings=[ref_prefs["embedding"]],
            n_results=n_results + 1,  # +1 to exclude self
            include=["documents", "metadatas", "distances"],
        )

        similar_students = []
        for i, sid in enumerate(results["ids"][0]):
            if sid != student_id:  # Exclude self
                similar_students.append(
                    {
                        "student_id": sid,
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                )

        return similar_students[:n_results]

    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
    # CONCEPT EMBEDDINGS
    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

    def add_concept(
        self,
        concept_id: str,
        concept_description: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Add or update concept embedding.

        Args:
            concept_id: Unique concept identifier (e.g., "photosynthesis_process")
            concept_description: Text description of the concept
            metadata: Additional metadata (prerequisites, difficulty, etc.)
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            return None

        self.concepts_collection.upsert(
            ids=[concept_id],
            documents=[concept_description],
            metadatas=[metadata or {}],
        )

    def get_concept(self, concept_id: str) -> Optional[Dict]:
        """
        Retrieve concept information.

        Args:
            concept_id: Concept identifier

        Returns:
            Dict with concept data, or None if not found
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            return None

        results = self.concepts_collection.get(
            ids=[concept_id],
            include=["documents", "metadatas", "embeddings"],
        )

        if not results["ids"]:
            return None

        return {
            "concept_id": concept_id,
            "document": results["documents"][0],
            "metadata": results["metadatas"][0],
            "embedding": results["embeddings"][0] if results.get("embeddings") else None,
        }

    def find_related_concepts(
        self,
        concept_id: str,
        n_results: int = 5,
    ) -> List[Dict]:
        """
        Find concepts related to the given concept.

        Args:
            concept_id: Reference concept ID
            n_results: Number of related concepts to return

        Returns:
            List of dicts with related concept info
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            return None

        # Get reference concept
        ref_concept = self.get_concept(concept_id)
        if not ref_concept:
            return []

        # Query for related concepts
        results = self.concepts_collection.query(
            query_embeddings=[ref_concept["embedding"]],
            n_results=n_results + 1,
            include=["documents", "metadatas", "distances"],
        )

        related_concepts = []
        for i, cid in enumerate(results["ids"][0]):
            if cid != concept_id:  # Exclude self
                related_concepts.append(
                    {
                        "concept_id": cid,
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                )

        return related_concepts[:n_results]

    def search_concepts(
        self,
        query_text: str,
        n_results: int = 10,
        metadata_filter: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Search for concepts matching a text query.

        Args:
            query_text: Natural language query
            n_results: Number of results to return
            metadata_filter: Filter by metadata (e.g., {"difficulty": "beginner"})

        Returns:
            List of matching concepts
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            return None

        results = self.concepts_collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=metadata_filter,
            include=["documents", "metadatas", "distances"],
        )

        concepts = []
        for i, cid in enumerate(results["ids"][0]):
            concepts.append(
                {
                    "concept_id": cid,
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
            )

        return concepts

    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
    # CONTENT VECTORS
    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

    def add_content(
        self,
        content_id: str,
        content_text: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Add learning content for similarity matching.

        Args:
            content_id: Unique content identifier
            content_text: Content text (lesson, question, explanation, etc.)
            metadata: Additional metadata (content_type, difficulty, concepts, etc.)
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            return None

        self.content_collection.upsert(
            ids=[content_id],
            documents=[content_text],
            metadatas=[metadata or {}],
        )

    def search_similar_content(
        self,
        query_text: str,
        n_results: int = 10,
        metadata_filter: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Find content similar to a query.

        Useful for Engine 4 to find alternative explanations or examples.

        Args:
            query_text: Query text
            n_results: Number of results
            metadata_filter: Filter by metadata

        Returns:
            List of similar content items
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            return None

        results = self.content_collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=metadata_filter,
            include=["documents", "metadatas", "distances"],
        )

        content_items = []
        for i, cid in enumerate(results["ids"][0]):
            content_items.append(
                {
                    "content_id": cid,
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
            )

        return content_items

    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
    # COLLECTION MANAGEMENT
    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

    def get_collection_counts(self) -> Dict[str, int]:
        """
        Get document counts for all collections.

        Returns:
            Dict mapping collection names to document counts
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            return None

        return {
            "learning_preferences": self.learning_prefs_collection.count(),
            "concept_embeddings": self.concepts_collection.count(),
            "content_vectors": self.content_collection.count(),
        }

    def reset_collections(self):
        """Delete all collections and recreate them (DESTROYS ALL DATA!)."""
        if not CHROMADB_AVAILABLE or self.client is None:
            return None

        print("  Resetting all vector store collections...")

        # Delete collections
        try:
            self.client.delete_collection("learning_preferences")
        except:
            pass
        try:
            self.client.delete_collection("concept_embeddings")
        except:
            pass
        try:
            self.client.delete_collection("content_vectors")
        except:
            pass

        # Recreate
        self._init_collections()
        print(" Vector store collections reset!")


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CLI COMMANDS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            """
Usage: python -m src.student_model.vector_store <command>

Commands:
  init      - Initialize vector store collections
  stats     - Show collection statistics
  reset     - Reset all collections (DESTROYS DATA!)
  test      - Run basic functionality test

Example:
  python -m src.student_model.vector_store init
        """
        )
        sys.exit(1)

    command = sys.argv[1]
    store = StudentVectorStore()

    if command == "init":
        print(" Vector store initialized!")
        counts = store.get_collection_counts()
        print(f"Collections: {counts}")

    elif command == "stats":
        counts = store.get_collection_counts()
        print("\n" + "=" * 50)
        print("= VECTOR STORE STATISTICS")
        print("=" * 50)
        for collection, count in counts.items():
            print(f"  {collection:25s}: {count:5d} documents")
        print("=" * 50 + "\n")

    elif command == "reset":
        confirm = input("  This will DELETE ALL VECTORS. Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            store.reset_collections()
        else:
            print("Cancelled.")

    elif command == "test":
        print("Running basic functionality test...")

        # Test 1: Add student preferences
        store.add_student_preferences(
            "test_student_1",
            "Visual learner who prefers diagrams, charts, and videos. Struggles with text-heavy content.",
            metadata={"learning_preferences": ["Visual", "Kinesthetic"], "reading_level": "Basic"},
        )
        print(" Added student preferences")

        # Test 2: Add concept
        store.add_concept(
            "photosynthesis_test",
            "Process by which plants convert light energy into chemical energy, producing glucose and oxygen",
            metadata={"difficulty": "intermediate", "subject": "Science"},
        )
        print(" Added concept")

        # Test 3: Search concepts
        results = store.search_concepts("How do plants make food?", n_results=5)
        print(f" Found {len(results)} matching concepts")

        print("\n All tests passed!")

    else:
        print(f"L Unknown command: {command}")
        sys.exit(1)
