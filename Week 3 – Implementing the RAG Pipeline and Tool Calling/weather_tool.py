from langchain_ollama import ChatOllama
from langchain_core.tools import Tool
import requests


def get_weather(city):

    url = f"https://wttr.in/{city}?format=3"

    response = requests.get(url)

    return response.text


weather_tool = Tool(
    name="WeatherTool",
    description="""
    Use this tool when the user asks about weather,
    temperature, climate, or forecast.

    Examples:
    weather in Karachi
    weather in Lahore
    temperature in Islamabad
    """,
    func=get_weather
)

llm = ChatOllama(
    model="llama3.1"
)



llm_with_tools = llm.bind_tools(
    [weather_tool]
)


question = input("Ask a question: ")


ai_msg = llm_with_tools.invoke(question)

print("\nLLM Response:")
print(ai_msg)

print("\n----------------------\n")


if ai_msg.tool_calls:

    tool_call = ai_msg.tool_calls[0]

    city = tool_call["args"]["__arg1"]

    print("Tool Selected:")
    print(tool_call["name"])

    print("\nTool Input:")
    print(city)

    result = weather_tool.invoke(city)

    print("\nTool Output:")
    print(result)

    print("\n----------------------\n")


    final = llm.invoke(
        f"""
        Use the following weather information:

        {result}

        Answer the user's question:

        {question}
        """
    )

    print("Final Answer:\n")
    print(final.content)

else:

    print("No tool call generated.\n")
    print(ai_msg.content)