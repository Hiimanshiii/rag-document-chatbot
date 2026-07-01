from langchain_core.prompts import ChatPromptTemplate

from app.retriever import get_retriever
from app.llm import get_llm


def ask_question(question):
    """
    Runs the complete RAG pipeline.
    """

    retriever = get_retriever()

    llm = get_llm()

    documents = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    prompt = ChatPromptTemplate.from_template(
        """
You are a helpful AI assistant.

Answer the user's question ONLY using the context below.

If the answer is not present in the context, say:
"I don't know based on the uploaded document."

Context:
{context}

Question:
{question}
"""
    )

    formatted_prompt = prompt.invoke(
    {
        "context": context,
        "question": question
    }
    )

    response = llm.invoke(formatted_prompt)

    return response.content

