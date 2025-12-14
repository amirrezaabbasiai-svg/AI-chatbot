from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

def get_response(prompt):
    llm = ChatOllama(
        model="llama3.1:8b",
        temperature=0.3,
        top_p=0.9,
    )
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    return response.content