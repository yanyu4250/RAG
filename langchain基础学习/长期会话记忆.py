import os,json
from typing import Sequence

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage

# message_to_dict:单个消息对象(BaseMessage类对象) --> 字典
#messages_from_dict：[字典，字典......] --> [BaseMessage类对象，BaseMessage类对象......](消息)
#AIMessage,HumanMessage,SystemMessage类都是BaseMessage类的子类
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory



class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self,session_id,storage_path):
        self.session_id = session_id        #会话id
        self.storage_path = storage_path    #不同会话id存储文件的文件夹路径
        self.file_path = os.path.join(self.storage_path,self.session_id )
        #os拼接文件路径，生成文件路径为./self.storage_path/self.session_id

        #确保文件夹存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        #os.makedirs(name:要创建的路径,exist_ok：True->如果目录已存在，不会报错；False ->如果目录已存在，抛出FileExistError错误)

    def add_messages(self,messages:Sequence[BaseMessage])-> None:       #将新的消息添加到会话中
        #Sequence序列：类似于list，tuple
        all_messages = list(self.messages)  #已有的消息列表
        all_messages.extend(messages)       #新的和已有的消息列表融合为一个列表

        #将数据同步写入到本地文件中
        #类对象写入文件 -> 一堆二进制
        #为了方便，将BaseMessage类对象转换为字典(借助json模块以json字符串写入文件)
        # message_to_dict:单个消息对象(BaseMessage类对象) --> 字典
        #new_messages = []
        #for messages in all_messages:
        #   d = message_to_dict(messages)   messages --> 字典
        #   new_messages.append(d)          d加入新的列表

        new_messages = [message_to_dict(messages) for messages in all_messages]
        #将数据写入文件
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump(new_messages,f)        #把数据转为json格式，写入文件

    @property       #通过@property装饰器，将messages方法变为成员属性
    def messages(self) -> list[BaseMessage]:        #获取会话中的所有消息，返回list[字典]类型
        #当前文件内： list[字典]
        try:
            with open(self.file_path,"r",encoding="utf-8") as f:
                messages_data =json.load(f)         #读取文件,返回值是：list[字典]
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump([],f)     #清空文件

model = ChatTongyi(model = "qwen3-max")
prompt = ChatPromptTemplate.from_messages(
    [
    ("system","你需要根据会话历史回应用户的问题，对话历史："),
    MessagesPlaceholder("chat_history"),
    ("human","请回答如下问题：{input}")
    ]
)
str_parser = StrOutputParser()

def print_prompt(full_prompt):  #检查输出的prompt
    print("="*20,full_prompt.to_string(),"="*20)
    return full_prompt

base_chain = prompt | print_prompt | model | str_parser


def get_history(session_id):
    return FileChatMessageHistory(session_id,"./chat_history")



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

    #res = conversation_chain.invoke({"input":"总共有几个宠物"},session_config)
    #print("第三次执行：",res)






