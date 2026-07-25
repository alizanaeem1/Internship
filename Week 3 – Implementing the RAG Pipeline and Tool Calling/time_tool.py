from langchain_ollama import ChatOllama
from langchain_core.tools import Tool
from datetime import datetime



def get_current_time(dummy_input):

    return datetime.now().strftime("%I:%M:%S %p")



time_tool = Tool(
    name="CurrentTime",
    description="""
    Use this tool when the user asks about
    current time.

    Examples:
    What time is it?
    Current time
    Tell me the time
    """,
    func=get_current_time
)



llm = ChatOllama(
    model="llama3.1"
)



llm_with_tools = llm.bind_tools(
    [time_tool]
)



question = "What's time rigt now"


ai_msg = llm_with_tools.invoke(question)

print("\nLLM Response:")
print(ai_msg)

print("\n----------------------\n")



if ai_msg.tool_calls:

    tool_call = ai_msg.tool_calls[0]

    result = time_tool.invoke(
        tool_call["args"]["__arg1"]
    )

    print("Tool Output:")
    print(result)

    print("\n----------------------\n")

    final = llm.invoke(
        f"""
        Use the following information:

        Current Time: {result}

        Answer the user's question:

        {question}
        """
    )

    print("Final Answer:\n")
    print(final.content)

else:

    print("No tool call generated.")
    print(ai_msg.content)