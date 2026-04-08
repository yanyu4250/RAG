from ollama import embeddings

md5_path = "D:\大模型学习\RAG项目\chroma_db"  #md5值存储路径(向量数据库存储位置)

#Chroma(向量数据库)
collection_name = "rag"             #向量数据库名称
persist_directory = "./chroma_db"   #数据库存储路径

#spliter
chunk_size = 1000
chunk_overlap = 100
separators = ["\n\n","\n","。","？","！","；","，","、"," ","",".",",","?","!"]
max_split_char_number = 1000

#相似度检索
similarity_threshold = 2            #检索返回的匹配文件数量

embedding_model_name = "text-embedding-v4"  #嵌入模型，将文本转换为向量
chat_model_name = "qwen3-max"               #聊天模型，理解问题并生成回复