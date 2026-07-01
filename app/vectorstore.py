from langchain_community.vectorstores import FAISS

from app.embeddings import get_embedding_model


def create_vector_store(chunks):
    """
    Converts document chunks into embeddings
    and stores them in FAISS.
    """

    embeddings = get_embedding_model()

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return vectorstore

def save_vector_store(vectorstore):
    """
    Saves the FAISS index to disk.
    """

    vectorstore.save_local("vectorstore")

def load_vector_store():
    """
    Loads the saved FAISS index from disk.
    """

    embeddings = get_embedding_model()

    vectorstore = FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore  