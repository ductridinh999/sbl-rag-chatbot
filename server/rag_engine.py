import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq 
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class SBLRAG:
    def __init__(self, debug=False):
        self.debug = debug
        # Setup Embeddings (Kept same as Indexer)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Connect to Pinecone
        self.vectorstore = PineconeVectorStore.from_existing_index(
            index_name="sbl-rag-chatbot",
            embedding=self.embeddings
        )
        self.retriever = self.vectorstore.as_retriever()
        
        # Setup LLM 
        # "llama-3.3-70b-versatile" 
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY") 
        )
        
        # Create the Chain
        system_prompt = (
            "You are a science-based fitness expert. "
            "Use the following context to answer the question. "
            "\n\n"
            "{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        self.rag_chain = create_retrieval_chain(self.retriever, question_answer_chain)

    def ask(self, query: str):
        response = self.rag_chain.invoke({"input": query})
        
        if self.debug:
            print("\n" + "="*50)
            print("RETRIEVED CONTEXT (DEBUG):")
            for i, doc in enumerate(response["context"]):
                print(f"\n--- Document {i+1} ---")
                print(f"Source: {doc.metadata.get('source', 'Unknown')}")
                print(f"Content: {doc.page_content}...")
            print("="*50 + "\n")

        return {
            "answer": response["answer"],
            "context": response["context"]
        }

# if __name__ == "__main__":
#     # Initialize with debug=True to see the context
#     bot = SBL(debug=True)
#     print("Testing Groq...")
#     result = bot.ask("What are the top 3 exercises for chest?")
    
#     print("RESPONSE:")
#     print(result["answer"])