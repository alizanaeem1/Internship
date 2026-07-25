from langchain_ollama import ChatOllama
from langchain_core.tools import Tool
import wikipediaapi


wiki = wikipediaapi.Wikipedia(
    user_agent="rag-tool",
    language="en"
)


def search_wikipedia(query):

    page = wiki.page(query)

    if page.exists():
        return page.summary

    return "No information found"


wiki_tool = Tool(
    name="Wikipedia",
    description="Search Wikipedia for information",
    func=search_wikipedia
)


llm = ChatOllama(
    model="llama3.1"
)


tools = [wiki_tool]

llm_with_tools = llm.bind_tools(tools)


question = "What  is Quaid-e-Azam?"


# first LLM decision
ai_msg = llm_with_tools.invoke(question)


# check tool call
if ai_msg.tool_calls:

    tool_call = ai_msg.tool_calls[0]

    result = wiki_tool.invoke(
        tool_call["args"]["__arg1"]
    )


    # give tool result back to LLM
    final = llm.invoke(
        f"""
        Answer the user question using this information:

        {result}

        Question:
        {question}
        """
    )

    print(final.content)

else:
    print(ai_msg.content)