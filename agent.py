from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
# from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
import pandas as pd
from langchain_anthropic import ChatAnthropic

from executor_tool import PythonToolWithResult
from prompts import SYSTEM_PROMPT

load_dotenv()

df = pd.read_csv("data/Allocations.csv")

memory = MemorySaver()
# llm = ChatBedrockConverse(
#     model="anthropic.claude-3-sonnet-20240229-v1:0",
#     temperature=0,
#     max_tokens=None,
#     # other params...
# )
# llm = ChatOpenAI(model="o3-mini")
#
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
    # other params...
)

tool = PythonToolWithResult(locals={"df": df})

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT.format(df_head=df.head(2).to_markdown())),
        ("placeholder", "{messages}"),
    ]
)

def state_modifier(state):
    return [{"role": "system", "content": SYSTEM_PROMPT.format(df_head=df.head().to_markdown())}] + state["messages"]

agent = create_react_agent(
    model=llm,
    tools=[tool],
    state_modifier=state_modifier,
    checkpointer=memory
)

def invoke_llm(human_msg: str, thread_id):
    # before new call - set last_result type as text
    # it will be changed if tool will be called, but if tool won't be
    # called - it will remain text
    if tool.last_result:
        tool.last_result.result = ""
        tool.last_result.type = "text"
        tool.last_result.code = ""
    llm_response = agent.invoke(
        {"messages": [("human", human_msg)]},
        config={"configurable": {"thread_id": thread_id}})
    return llm_response, tool.last_result


if __name__ == '__main__':
    # q = "What is average raise?"
    # q = "Show me all low performers that received a high raise"
    q = "Show graph with anomalies regarding employees compensation and/or performance"
    response = invoke_llm(q)
    print(response)