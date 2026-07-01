from app.vectorstore import load_vector_store


def get_retriever():
    """
    Loads the FAISS vector store
    and returns a retriever.
    """

    vectorstore = load_vector_store()

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    return retriever