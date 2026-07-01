import streamlit as st
import requests
import os

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)



st.set_page_config(
    page_title="Chat With Your Docs",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

# Sidebar for PDF upload and server status
with st.sidebar:
    st.header("📁 Document Upload")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    # Upload button
    upload_clicked = st.button("Upload PDF", use_container_width=True)
    
    if upload_clicked:
        if uploaded_file is None:
            st.error("Please select a PDF file first.")
        else:
            with st.spinner("Uploading and processing PDF..."):
                try:
                    # Prepare file payload
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    }
                    # Send POST request to FastAPI backend
                    response = requests.post(
                        f"{BACKEND_URL}/upload",
                        files=files,
                        timeout=90  # Generous timeout for processing/indexing
                    )
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        if "error" in res_data:
                            st.error(f"Upload failed: {res_data['error']}")
                        else:
                            st.success(res_data.get("message", "File uploaded successfully!"))
                            st.session_state.document_uploaded = True
                            # Clear chat when a new document is successfully loaded
                            st.session_state.messages = []
                    else:
                        st.error(f"Server error: Received status code {response.status_code}")
                
                except requests.exceptions.Timeout:
                    st.error("Upload timeout. The server took too long to process the PDF.")
                except requests.exceptions.ConnectionError:
                    st.error("Backend unavailable. Make sure the FastAPI server is running on http://127.0.0.1:8000")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

# Right main chat area
st.title("📄 Chat With Your Documents")
st.subheader("Upload a PDF and ask questions about it using AI.")

# Action bar above the chat area
col_clear, _ = st.columns([1, 4])
with col_clear:
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User query input
if not st.session_state.document_uploaded:
    st.info("📄 Please upload a PDF before asking questions.")
    st.chat_input("Ask a question about the uploaded document...", disabled=True)
else:
    if user_query := st.chat_input("Ask a question about the uploaded document..."):
        # Append user query to history and display it immediately
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
        
    # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching and generating answer..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/ask",
                        json={"question": user_query},
                        timeout=60
                    )
                
                    if response.status_code == 200:
                        res_data = response.json()
                        answer = res_data.get("answer", "No answer returned.")
                        st.write(answer)
                        # Append answer to history
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        error_msg = f"Server returned error code {response.status_code}."
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": f"Error: {error_msg}"})
                    
                except requests.exceptions.Timeout:
                    error_msg = "Request timed out while waiting for a response."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {error_msg}"})
                except requests.exceptions.ConnectionError:
                    error_msg = "Backend unavailable. Make sure the FastAPI server is running on http://127.0.0.1:8000"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {error_msg}"})
                except Exception as e:
                    error_msg = f"An unexpected error occurred: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {error_msg}"})
