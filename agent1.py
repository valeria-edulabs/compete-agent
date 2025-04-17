from pprint import pprint

from langgraph.prebuilt import create_react_agent
from langchain_aws import ChatBedrockConverse
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent, create_csv_agent
from langchain_experimental.tools import PythonAstREPLTool
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate

from prompts import PROMPT_PREFIX, PROMPT_PREFIX_1, SYSTEM_PROMPT
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser

load_dotenv()

df = pd.read_csv("data/Allocations.csv")

llm = ChatBedrockConverse(
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    temperature=0,
    max_tokens=None,
    # other params...
)

# llm = ChatOpenAI(model="o3-mini")






tool = PythonAstREPLTool(locals={"df": df})
llm_with_tools = llm.bind_tools([tool], tool_choice=tool.name)

parser = JsonOutputKeyToolsParser(key_name=tool.name, first_tool_only=True)




prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | llm_with_tools | parser | tool

def invoke_llm(
        text,
        history,
        # df
):
    response = chain.invoke({
        "question": text,
        "history": history,
        "df_head": df.head().to_markdown()
    })
    print(type(response))
    pprint(response)
    return response

q = "What is average raise?"
q = "Show me all low performers that received a high raise"
q = "Show graph with anomalies regarding employees compensation and/or performance"
response = chain.invoke({"question": q, "df_head": df.head().to_markdown()})
print(type(response))
pprint(response)
