from langchain_core.prompts import ChatPromptTemplate

system_prompt = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Only provide the answer and nothing else!
"""

human_prompt = """
Question: {question}

Context: 
{context}

Answer:
"""

rag_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", human_prompt),
    ]
)

