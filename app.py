import os
import streamlit as st
from qdrant_client import QdrantClient
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Setup Qdrant Client
qdrant_path = os.getenv("QDRANT_PATH", "./qdrant_db")
try:
    qdrant_client = QdrantClient(path=qdrant_path)
    qdrant_client.set_model("BAAI/bge-small-en-v1.5")
except Exception as e:
    st.error(f"Error connecting to Qdrant: {e}. Please run ingest.py first.")
    st.stop()

# Setup Groq Client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY not found in .env file.")
    st.stop()

groq_client = Groq(api_key=groq_api_key)

COLLECTION_NAME = "de_knowledge"

st.set_page_config(page_title="DE Copilot", page_icon="🗄️", layout="wide")

st.title("🗄️ Data Engineering (DE) Copilot")
st.markdown("Ask questions about data framing, deduplication, schemas, and more.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("How do we handle deduplication?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # 1. Retrieve context from Qdrant
        with st.spinner("Searching knowledge base..."):
            try:
                search_result = qdrant_client.query(
                    collection_name=COLLECTION_NAME,
                    query_text=prompt,
                    limit=3
                )
            except Exception as e:
                st.error("Could not query database. Did you run ingest.py?")
                st.stop()
            
            context_blocks = []
            citations = []
            for hit in search_result:
                source = hit.metadata.get('source', 'Unknown')
                content = hit.document
                context_blocks.append(f"--- SOURCE: {source} ---\n{content}\n")
                citations.append(source)
                
            context_text = "\n".join(context_blocks)
        
        # 2. Build Prompt for Groq
        system_prompt = f"""You are an expert Data Engineering Copilot.
Your job is to answer the user's question using ONLY the provided context from the data warehouse codebase and documentation.
If the answer is not in the context, politely say you don't know based on the provided documents.
Be concise, and include code snippets if relevant.

CONTEXT:
{context_text}
"""
        
        messages_for_llm = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add history
        for msg in st.session_state.messages[-4:]: # Keep last 4 messages for context
            messages_for_llm.append({"role": msg["role"], "content": msg["content"]})
            
        # 3. Stream from Groq LLM
        with st.spinner("Generating answer..."):
            try:
                stream = groq_client.chat.completions.create(
                    messages=messages_for_llm,
                    model="llama-3.1-8b-instant", # Updated supported model
                    temperature=0.2,
                    stream=True,
                )
                
                full_response = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                # Append citations
                if citations:
                    unique_citations = list(set(citations))
                    full_response += f"\n\n**Sources:** {', '.join(unique_citations)}"
                    
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"Error generating response: {e}"
                message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
