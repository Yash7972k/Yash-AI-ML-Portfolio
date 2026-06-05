import os
import re
from collections import Counter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from google import genai
from dotenv import load_dotenv
from transformers import AutoTokenizer, T5ForConditionalGeneration

load_dotenv()

FAISS_INDEX_PATH = "faiss_index"
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")  # Free tier model
session_store = {}


def _normalize_tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _keyword_overlap(question: str, text: str) -> int:
    q_tokens = Counter(_normalize_tokens(question))
    t_tokens = Counter(_normalize_tokens(text))
    return sum((q_tokens & t_tokens).values())


def get_local_fallback_answer(question: str, docs: list) -> tuple[str, list[str]]:
    """Provide a simple local answer using the retrieved notes when Gemini quota is exhausted."""
    if not docs:
        return (
            "I could not find this in your notes. The Gemini quota is currently exhausted, so I switched to a local retrieval fallback.",
            [],
        )

    scored = []
    for doc in docs:
        text = doc.page_content or ""
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        for sentence in sentences[:4]:
            scored.append((
                _keyword_overlap(question, sentence),
                sentence,
                doc.metadata.get("source", "notes.pdf"),
            ))

    scored.sort(key=lambda item: item[0], reverse=True)
    best_sentence = scored[0][1] if scored else ""
    sources = list(dict.fromkeys(item[2] for item in scored[:4]))

    if not best_sentence:
        answer = "I could not find a clear match in your uploaded notes."
    else:
        answer = (
            "I’m using the local fallback answer because Gemini quota is exhausted. "
            f"Based on your notes: {best_sentence}"
        )

    return answer, sources


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]


def load_and_chunk_pdfs(pdf_paths: list) -> list:
    all_docs = []
    for path in pdf_paths:
        loader = PyMuPDFLoader(path)
        docs = loader.load()
        all_docs.extend(docs)
    # Increased chunk size to get more diverse context and reduce repetition
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
    return splitter.split_documents(all_docs)


def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def build_vector_store(chunks):
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(FAISS_INDEX_PATH)
    return vector_store


def load_vector_store():
    embeddings = get_embeddings()
    return FAISS.load_local(
        FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
    )


class LocalFreeChain:
    """A free local answer path that uses a tiny Hugging Face model with no API key."""

    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.tokenizer = None
        self.model = None

    def _load_model(self):
        """Lazy-load the model only when first needed."""
        if self.tokenizer is None:
            self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
            self.model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")
            self.model.eval()

    def invoke(self, input_data, config=None):
        import torch
        
        self._load_model()  # Lazy-load on first invoke
        question = input_data.get("input", "") if isinstance(input_data, dict) else str(input_data)
        
        # Retrieve relevant documents
        retriever = self.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        docs = retriever.invoke(question)
        
        # Build comprehensive context from all retrieved docs (limit to avoid truncation)
        context_parts = []
        total_chars = 0
        MAX_CONTEXT_CHARS = 2500  # Limit context to prevent truncation
        
        for doc in docs:
            page_content = getattr(doc, "page_content", "")
            if page_content.strip():
                if total_chars + len(page_content) <= MAX_CONTEXT_CHARS:
                    context_parts.append(page_content.strip())
                    total_chars += len(page_content)
                else:
                    break
        
        context = "\n\n".join(context_parts)
        
        if not context:
            return "I could not find relevant information in your notes to answer this question."

        # Create a focused prompt for T5
        prompt = f"Answer based on context:\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"

        # Tokenize with better handling
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512  # Reasonable limit
        )
        
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=256,
                min_length=15,
                do_sample=True,  # Enable sampling for better answers
                temperature=0.8,  # Now this will be used
                top_p=0.95,
                num_beams=1,  # Greedy search with sampling
                early_stopping=True,
            )

        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        
        # Clean up answer - remove any artifacts
        answer = re.sub(r'\s+', ' ', answer)  # Remove extra whitespace
        
        # If answer is too short or just repeats question, provide context
        if not answer or len(answer) < 10 or question.lower() in answer.lower():
            # Return first sentence from context as fallback
            sentences = re.split(r'(?<=[.!?])\s+', context_parts[0]) if context_parts else []
            answer = sentences[0] if sentences else "No relevant information found."
        
        return answer


class LocalFallbackChain:
    """Simple note-based fallback used if the local model is unavailable."""

    def __init__(self, vector_store):
        self.vector_store = vector_store

    def invoke(self, input_data, config=None):
        question = input_data.get("input", "") if isinstance(input_data, dict) else str(input_data)
        retriever = self.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        docs = retriever.invoke(question)
        answer, _ = get_local_fallback_answer(question, docs)
        return answer


def get_rag_chain(vector_store):
    use_local_provider = os.getenv("USE_LOCAL_PROVIDER", "true").lower() not in ("false", "0", "no")
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    if use_local_provider:
        try:
            return LocalFreeChain(vector_store)
        except Exception:
            return LocalFallbackChain(vector_store)

    if not api_key:
        raise ValueError("Missing Gemini API key. Add GOOGLE_API_KEY to your .env file or set USE_LOCAL_PROVIDER=true.")

    # Set API key for google-genai package
    os.environ["GOOGLE_API_KEY"] = api_key

    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        google_api_key=api_key,
        temperature=0.3
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 6}  # Increased from 4 to get more diverse context
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful study assistant. Answer the question using ONLY the context below.\n"
         "If the answer is not in the context, say 'I could not find this in your notes.'\n\n"
         "Context:\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    rag_chain = (
        RunnablePassthrough.assign(
            context=RunnableLambda(lambda x: format_docs(retriever.invoke(x["input"])))
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    conversational_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    # Attach vector_store using a wrapper to avoid Pydantic errors
    class ChainWrapper:
        def __init__(self, chain, vs):
            self.chain = chain
            self.vector_store = vs
        def invoke(self, *args, **kwargs):
            return self.chain.invoke(*args, **kwargs)
    
    return ChainWrapper(conversational_chain, vector_store)


def ask_question(chain, question: str, session_id: str = "default") -> dict:
    use_local_provider = os.getenv("USE_LOCAL_PROVIDER", "true").lower() not in ("false", "0", "no")

    try:
        # If using LocalFreeChain or LocalFallbackChain, invoke directly
        if isinstance(chain, (LocalFreeChain, LocalFallbackChain)):
            chain_type = type(chain).__name__
            answer = chain.invoke({"input": question})
            return {"answer": answer, "sources": [], "error": None, "chain_type": chain_type}
        
        # For Gemini chain or ChainWrapper, extract the actual chain
        actual_chain = chain.chain if hasattr(chain, 'chain') else chain
        
        # Invoke with session history
        answer = actual_chain.invoke(
            {"input": question},
            config={"configurable": {"session_id": session_id}}
        )
        return {"answer": answer, "sources": [], "error": None, "chain_type": "Gemini"}
    except Exception as exc:
        error_msg = str(exc)
        
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg or "quota" in error_msg.lower():
            retriever = getattr(chain, "vector_store", None)
            if retriever is not None:
                docs = retriever.as_retriever(search_type="similarity", search_kwargs={"k": 4}).invoke(question)
                answer, sources = get_local_fallback_answer(question, docs)
                return {
                    "answer": answer,
                    "sources": sources,
                    "error": "quota_exhausted",
                    "chain_type": "FallbackChain",
                }
            return {
                "answer": (
                    "⚠️ Gemini quota has been exhausted (429). "
                    "Please enable billing in Google AI Studio or wait for the free-tier limit to reset, then try again."
                ),
                "sources": [],
                "error": "quota_exhausted",
                "chain_type": "Error",
            }
        return {
            "answer": f"❌ Error: {error_msg}",
            "sources": [],
            "error": "other",
            "chain_type": "Error",
        }