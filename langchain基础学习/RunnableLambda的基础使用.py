from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

#创建所需容器
str_parser = StrOutputParser ()
json_parser = JsonOutputParser ()

#创建模型
model = ChatTongyi(model = "qwen3-max")

#第一个提示词模板
first_prompt = PromptTemplate.from_template(
    "我邻居姓:{lastname},刚生了{gender}，请帮忙起一个名字，仅回复我起的名字。"
    "并封装成json格式。要求key是name，value是你起的名字，请遵循我的要求。"
)

#第二个提示词模板
second_prompt = PromptTemplate.from_template(
    "姓名:{name},请帮我解析含义。"
)

#创建匿名方法 函数的入参：AIMessage --> dict({"name":"value"})
my_func = RunnableLambda(lambda ai_message: ai_message.content)

#构建链
chain = first_prompt | model | my_func | second_prompt | model | str_parser

for chunk in chain.stream({"lastname":"张","gender":"女"}):
    print(chunk,end="",flush=True)