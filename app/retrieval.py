import os
import json
from dotenv import load_dotenv

load_dotenv()

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_vectorstore():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX")
    index = pc.Index(index_name)
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=768
    )
    
    return PineconeVectorStore(
        index=index,
        embedding=embeddings,
        text_key="text",
        namespace="sop"
    )

def stream_answer(question: str):
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, streaming=True)
    
    docs = retriever.invoke(question)
    sources = [doc.metadata.get("source", "Unknown") for doc in docs]
    
    context_text = "\n\n".join([doc.page_content for doc in docs])
    
    template = """You are a strict, highly accurate corporate AI assistant for DocuMind.
Your primary directive is to answer the user's question using ONLY the provided Context.

CRITICAL RULES:
1. If the exact answer is not explicitly written in the Context below, you MUST refuse to answer and reply ONLY with: "This is outside my scope."
2. Do not rely on outside knowledge.
3. Do not invent, guess, or fabricate facts.

Context: {context}

Question: {question}
Answer:"""

    prompt = PromptTemplate.from_template(template)
    
    chain = prompt | llm | StrOutputParser()
    
    def generate():
        yield json.dumps({"type": "metadata", "sources": list(set(sources))}) + "\n"
        
        for chunk in chain.stream({"context": context_text, "question": question}):
            yield json.dumps({"type": "content", "content": chunk}) + "\n"
            
    return generate()
