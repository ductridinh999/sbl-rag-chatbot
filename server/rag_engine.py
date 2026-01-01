import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq 
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class SBLRAG:
    def __init__(self, debug=False):
        self.debug = debug
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # Warm up
        try:
            print("Warming up embedding model...")
            self.embeddings.embed_query("warmup")
            print("Embedding model ready.")
        except Exception as e:
            print(f"Warmup warning: {e}")

        self.vectorstore = PineconeVectorStore.from_existing_index(
            index_name="sbl-rag-chatbot",
            embedding=self.embeddings
        )
        self.retriever = self.vectorstore.as_retriever()
        
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY") 
        )
        
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, contextualize_q_prompt
        )
        
        system_prompt = (
            "You are a science-based fitness expert. "
            "You have access to a knowledge base of fitness articles (provided below as Context). "
            "Use this Context to answer the user's question directly and naturally. "
            "\n\n"
            "Rules:"
            "\n1. If the user greets you (e.g., 'Hello', 'Hi'), ignore the Context and respond politely, asking how you can help."
            "\n2. Do NOT start your response with 'According to the text' or 'Based on the documents'."
            "\n3. Do NOT mention that you were provided with a text or context. Present the information as your own expert knowledge."
            "\n4. If the Context is not relevant to the question, answer from your general knowledge but mention you are using general knowledge."
            "\n\n"
            "Context from Knowledge Base:"
            "\n{context}"
        )
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        
        self.rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    def ask(self, query: str, history: list = []):
        chat_history = []
        for msg in history:
            if msg['role'] == 'user':
                chat_history.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                chat_history.append(AIMessage(content=msg['content']))

        response = self.rag_chain.invoke({
            "input": query,
            "chat_history": chat_history
        })
        
        if self.debug:
            print(f"DEBUG: Processing with {len(chat_history)} history items.")

        return {
            "answer": response["answer"],
            "context": response["context"]
        }