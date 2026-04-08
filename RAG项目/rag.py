
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from file_history_store import get_history



def print_prompt(prompt):
    print(prompt.to_string())
    return prompt

class RagService(object):
    def __init__(self):
        #向量存储服务
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name),
        )
        #提示词模板
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的参考资料为主，"
                 "简洁和专业的回答用户问题，参考资料{context}。"),
                ("system","并且我提供用户的历史对话记录如下："),
                MessagesPlaceholder("history"),         #占位，添加历史对话记录
                ("human", "请回答用户提问：{input}"),
            ]
        )
        #调用聊天模型
        self.chat_model = ChatTongyi(model=config.chat_model_name)
        #组装执行链
        self.chain = self.__get_chain()

    def __get_chain(self):
        """获取最终执行链"""
        retriever = self.vector_service.get_retriever()     #获取向量库的检索器


        def format_document(docs: list[Document]):      #处理检索器的输出内容
            if not docs:
                return "无相关参考资料"

            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"

            return formatted_str

        #增强链运行时会加入一个字典，返回多个字典值，提取input对应的值
        #为检索器做格式化
        def format_for_retriever(value:dict) :
            return value["input"]

        #为提示词做格式化
        def format_for_prompt_template(value:dict):
            #拼接成{input,context,history}
            new_value = {}
            new_value["input"] = value["input"]["input"]        #为什么用嵌套字典
            new_value["context"] = value["context"]
            new_value["history"] = value["input"]["history"]
            return new_value

        chain = (
            {
                "input":RunnablePassthrough(),
                "context": RunnableLambda(format_for_retriever)  | retriever | format_document
            }  | RunnableLambda(format_for_prompt_template) | self.prompt_template | print_prompt | self.chat_model | StrOutputParser()
            #检索器 | 处理输出的方法 |提示词模板 | 调用模型 | 输出解析器
        )

        #拥有历史会话记录的增强链
        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history"
        )


        return conversation_chain

if __name__ == '__main__':
    #session_id配置
    session_config = {
        "configurable":{
            "session_id":"user_001",
        }
    }
    res = RagService().chain.invoke({"input":"春天穿什么衣服"},session_config)
    print(res)