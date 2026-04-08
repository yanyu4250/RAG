from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

model = ChatTongyi(model = "qwen3-max")
prompt = PromptTemplate.from_template(
    "你需要根据会话历史回应用户的问题，会话历史:{chat_history},用户提问:{input},请回答问题。"
    )
str_parser = StrOutputParser()

def print_prompt(full_prompt):
    print("="*20,full_prompt.to_string(),"="*20)
    return full_prompt

base_chain = prompt | print_prompt | model | str_parser

store = {}      #字典格式，key就是session，value就是InMemoryChatMessageHistory类对象
#实现通过会话id获取INMemoryChatMessageHistory类对象的函数
def get_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


#创建一个新的链对原有链功能增强，能附带历史消息
conversation_chain = RunnableWithMessageHistory(
    base_chain,     #被增强的链
    get_history,    #通过会话id获取INMemoryChatMessageHistory类对象
    input_messages_key="input",             #表示用户输入在prompt中的占位符
    history_messages_key="chat_history"     #表示历史消息在prompt中的占位符
)

if __name__ == "__main__":
    #固定格式，添加langchain的配置，为当前程序配置所属的session_id
    session_config = {
        "configurable":{
            "session_id":"user_001"
        }
     }

    res = conversation_chain.invoke({"input":"小明有两个猫"},session_config)
    print("第一次执行：",res)

    res = conversation_chain.invoke({"input":"小刚有两只狗一只猫"},session_config)
    print("第二次执行：",res)

    res = conversation_chain.invoke({"input":"总共有几个宠物"},session_config)
    print("第三次执行：",res)
