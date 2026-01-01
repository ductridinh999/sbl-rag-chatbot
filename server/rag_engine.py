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
            "Answer the question directly and naturally using the provided context. "
            "Do not start your response with phrases like 'According to the text', 'Based on the context', or 'The documents say'. "
            "Instead, synthesize the information and present it as your own expert advice."
            "\n\n"
            "{context}"
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