from langchain_chroma import Chroma
import config_data as config

#向量存储检索服务
class VectorStoreService(object):
    def __init__(self,embedding):
        """

        :param embedding: 传入嵌入模型
        """

        self.embedding = embedding
        self.vector_store = Chroma(                     #创建向量存储实例
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory
        )

    def get_retriever(self):
        """返回向量检索器，方便加入chain"""
        return self.vector_store.as_retriever(search_kwargs={"k": config.similarity_threshold})   #每次检索返回几个匹配的结果

