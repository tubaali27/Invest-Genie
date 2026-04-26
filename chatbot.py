from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize the same embedding model used during document loading
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Load the existing vector store
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

# Create a retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Initialize the chat model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

# Create memory for conversation history
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

# Create a custom prompt template for conversational retrieval
prompt_template = """
You are a helpful assistant that answers questions based on the provided context from the document and conversation history.
Use the following pieces of context to answer the question. Consider the chat history for context.
If you don't know the answer based on the context, just say that you don't know.

Context from document:
{context}

Chat History:
{chat_history}

Current Question: {question}

Answer:
"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "chat_history", "question"]
)

# Create the ConversationalRetrievalChain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": PROMPT}
)

def chat_with_document():
    print("StockGenie Document Chatbot with Memory")
    print("Ask questions about your document. Type 'quit' to exit.")
    print("Type 'history' to see conversation history.")
    print("Type 'clear' to clear conversation history.\n")
    
    while True:
        question = input("You: ")
        
        if question.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        if question.lower() == 'history':
            print("\n📝 Conversation History:")
            chat_history = memory.chat_memory.messages
            if not chat_history:
                print("No conversation history yet.")
            else:
                for i, message in enumerate(chat_history):
                    role = "You" if message.type == "human" else "Bot"
                    print(f"{role}: {message.content}")
            print("-" * 50)
            continue
            
        if question.lower() == 'clear':
            memory.clear()
            print("✅ Conversation history cleared!")
            print("-" * 50)
            continue
            
        try:
            # Get response from the chain
            result = qa_chain({"question": question})
            
            # Print the answer
            print(f"\nBot: {result['answer']}")
            
            # Optionally show source documents
            print(f"📚 Sources used: {len(result['source_documents'])} document chunks")
            
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 50)


if __name__ == "__main__":
    # Choose which version to run
    chat_with_document()  # Advanced version with LangChain memory
    # simple_chat_with_history()  # Simple version with manual history