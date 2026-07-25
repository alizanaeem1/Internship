from langchain_ollama import ChatOllama
from langchain_core.tools import Tool
import requests


API_KEY = "1786e0287b5881fd6ce0eadd"

def exchange_currency(query):


    base, target = query.split(" to ")

    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base}"

    response = requests.get(url)

    data = response.json()

    rate = data["conversion_rates"][target]

    return f"1 {base} = {rate} {target}"


currency_tool = Tool(
    name="CurrencyExchange",
    description="""
    Use this tool when the user asks about currency conversion
    or exchange rates.

    Examples:
    USD to PKR
    EUR to USD
    GBP to PKR
    """,
    func=exchange_currency
)




llm = ChatOllama(
    model="llama3.1"
)




llm_with_tools = llm.bind_tools(
    [currency_tool]
)



question = "What is the USD to PKR exchange rate?"




ai_msg = llm_with_tools.invoke(question)

print("\nLLM Response:")
print(ai_msg)

print("\n----------------------\n")



if ai_msg.tool_calls:

    tool_call = ai_msg.tool_calls[0]

    query = tool_call["args"]["__arg1"]

    print("Tool Selected:")
    print(tool_call["name"])

    print("\nTool Input:")
    print(query)

    result = currency_tool.invoke(query)

    print("\nTool Output:")
    print(result)

    print("\n----------------------\n")


    final = llm.invoke(
        f"""
        Use the following currency information:

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