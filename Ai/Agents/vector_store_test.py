import os
import uuid
from google import genai
from google.cloud import storage
from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore
import vertexai
from vertexai import rag

PROJECT_ID = "ultimate-figure-447502-u3"
LOCATION = "us-central1"

CORPUS_NAME = "projects/ultimate-figure-447502-u3/locations/us-central1/ragCorpora/6917529027641081856"

# ── Initialize clients ──────────────────────────────────────────────────────────
vertexai.init(project=PROJECT_ID, location=LOCATION)
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
storage_client = storage.Client(project=PROJECT_ID)

# ── 1) Direct Retrieval Query ───────────────────────────────────────────────────
retrieval_config = rag.RagRetrievalConfig(
    top_k=5,
    filter=rag.Filter(vector_distance_threshold=0.5)
)

retrieval_response = rag.retrieval_query(
    rag_resources=[ rag.RagResource(rag_corpus=CORPUS_NAME) ],
    text="الخطب الخاصة بالمجتمع و حالات الزواج والطلاق ",
    rag_retrieval_config=retrieval_config
)

print("=== Raw Retrieved Chunks ===")
for i, ctx in enumerate(retrieval_response.contexts.contexts, start=1):
    print(f"\n--- Chunk #{i} ---")
    print(ctx.text)

# ── 2) Build a RAG Retrieval Tool for LLM ───────────────────────────────────────
# Fix: Use the correct way to create a retrieval tool
rag_tool = Tool(
    retrieval=Retrieval(
        source=VertexRagStore(
            rag_corpora=[CORPUS_NAME],
            rag_retrieval_config=retrieval_config
        )
    )
)

# ── 3) Generate a Grounded Response with Gemini ────────────────────────────────
model = genai.models.get("gemini-2.0-flash-001")

response = model.generate_content(
    contents="Based on the retrieved context, summarize what RAG is and why it's useful.",
    config=GenerateContentConfig(tools=[rag_tool])
)

print("\n=== LLM Grounded Response ===")
print(response.text)

# ── 4) Alternative: Using Vertex AI RAG directly ──────────────────────────────
# If the above doesn't work, try this approach
try:
    # Alternative method using Vertex AI RAG
    from vertexai.preview.generative_models import GenerativeModel
    
    # Create a model with RAG
    model_with_rag = GenerativeModel(
        "gemini-2.0-flash-001",
        tools=[
            Tool(
                retrieval=Retrieval(
                    source=VertexRagStore(
                        rag_corpora=[CORPUS_NAME],
                        rag_retrieval_config=retrieval_config
                    )
                )
            )
        ]
    )
    
    response_alt = model_with_rag.generate_content(
        "Based on the retrieved context about marriage and divorce speeches, provide a comprehensive summary."
    )
    
    print("\n=== Alternative RAG Response ===")
    print(response_alt.text)
    
except Exception as e:
    print(f"\nAlternative method failed: {e}")

# ── 5) Manual RAG Implementation ──────────────────────────────────────────────
# If both above methods fail, use manual RAG
def manual_rag_query(query_text, corpus_name, retrieval_config):
    """Manual RAG implementation"""
    # Get relevant chunks
    retrieval_response = rag.retrieval_query(
        rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
        text=query_text,
        rag_retrieval_config=retrieval_config
    )
    
    # Build context from retrieved chunks
    context = "\n\n".join([ctx.text for ctx in retrieval_response.contexts.contexts])
    
    # Create prompt with context
    prompt = f"""
    Based on the following context, answer the question: {query_text}
    
    Context:
    {context}
    
    Answer:
    """
    
    # Generate response without RAG tool
    model = genai.models.get("gemini-2.0-flash-001")
    response = model.generate_content(prompt)
    
    return response.text

# Use manual RAG as fallback
print("\n=== Manual RAG Response ===")
manual_response = manual_rag_query(
    "الخطب الخاصة بالمجتمع و حالات الزواج والطلاق",
    CORPUS_NAME,
    retrieval_config
)
print(manual_response)