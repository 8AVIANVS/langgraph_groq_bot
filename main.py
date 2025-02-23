from typing import Annotated

from typing_extensions import TypedDict

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

llm = ChatGroq(temperature=0, model_name="deepseek-r1-distill-llama-70b")

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

messages = []

def stream_graph_updates(user_input: str):
    # Add the new message to our history
    messages.append({"role": "user", "content": user_input})
    
    # Stream the graph with all messages
    for event in graph.stream({"messages": messages}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
            # Update our message history with all messages including the response
            messages.clear()
            messages.extend(value["messages"])

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() == "quit":
            print("Bye!")
            break

        stream_graph_updates(user_input)
    except:
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break