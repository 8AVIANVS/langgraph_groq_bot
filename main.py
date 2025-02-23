from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

messages = []

def stream_graph_updates(user_input: str):
    # Add the new message to our history
    messages.append(HumanMessage(content=user_input))
    # print("\nBefore graph.stream, messages:", [{"role": m.type, "content": m.content} for m in messages])
    
    # Stream the graph with all messages
    for event in graph.stream({"messages": messages}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
            # print("Graph state messages:", [{"role": m.type, "content": m.content} for m in value["messages"]])
            # Add only the new assistant message to our history
            messages.append(value["messages"][-1])
            # print("After update, messages:", [{"role": m.type, "content": m.content} for m in messages])

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