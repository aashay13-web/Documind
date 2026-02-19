from typing import Dict, Any
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores.pinecone import Pinecone as PineconeVS

from pinecone import Pinecone
try:
    from .config import settings
except ImportError:
    from config import settings

SYSTEM_PROMPT = """
You are DocuMind Enterprise, a corporate SOP assistant.

CRITICAL RULES:
- Answer ONLY using the information provided in the context.
- If the answer is not in the context, say: "I don't know. This is outside my scope."
- Do not use any external knowledge or assumptions.
- Always include brief source citations using the metadata (document name, page if available).

Context:
{context}

Question: {question}
"""

def get_vectorstore(namespace: str = "sop"):
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )
    # Initialize Pinecone client
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index)
    
    return PineconeVS(
        index=index,
        embedding=embeddings,
        text_key="text",
        namespace=namespace,
    )

def build_retrieval_chain(namespace: str = "sop"):
    vs = get_vectorstore(namespace)
    retriever = vs.as_retriever(search_kwargs={"k": 5})

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=SYSTEM_PROMPT,
    )

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
        api_key=settings.openai_api_key,
    )

    # Build a simple retrieval chain using LCEL
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    chain = (
        {"context": retriever | format_docs, "question": lambda x: x["question"]}
        | prompt
        | llm
    )
    return {"chain": chain, "retriever": retriever}

def answer_question(question: str, namespace: str = "sop") -> Dict[str, Any]:
    chain_data = build_retrieval_chain(namespace)
    chain = chain_data["chain"]
    retriever = chain_data["retriever"]
    
    # Get the answer from the chain
    answer = chain.invoke({"question": question})
    
    # Get source documents
    source_docs = retriever.invoke(question)
    sources = []
    for doc in source_docs:
        meta = doc.metadata
        sources.append(
            {
                "source": meta.get("source", ""),
                "page": meta.get("page", None),
                "chunk_id": meta.get("chunk_id", None),
            }
        )
    return {"answer": answer.content if hasattr(answer, "content") else str(answer), "sources": sources}