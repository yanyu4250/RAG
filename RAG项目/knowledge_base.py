"""
知识库
"""
import os
from ollama import embeddings
from sqlalchemy.testing.suite.test_reflection import metadata
from sqlalchemy.util import md5_hex
from sympy.physics.units import length
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

def check_md5(md5_str: str):
    """检查传入的md5函数是否已经被处理过了
        :return False(md5未被处理过) True(已经处理过，已有记录)
    """
    if not os.path.exists(config.md5_path):
        #if进入表示文件不存在
        open(config.md5_path,"w",encoding="utf-8").close()
        return  False
    else:
        for line in open(config.md5_path,"r",encoding="utf-8").readlines():
            line = line.strip() #去掉换行符和空格
            if line == md5_str:
                return True     #已经处理过
        return  False


def save_md5(md5_str: str):
    """保存md5函数"""
    with open(config.md5_path,"a",encoding="utf-8") as f:
        f.write(md5_str + "\n")


def get_string_md5(input_str: str,encoding="utf-8"):
    """将传入的字符串转换为md5字符串"""

    str_bytes = input_str.encode(encoding=encoding)    #将字符串转换为bytes字节数组
    md5_obj = hashlib.md5()         #创建md5对象
    md5_obj.update(str_bytes)       #更新内容(传入即将要转换的字节数组)
    md5_hex = md5_obj.hexdigest()   #得到md5的十六进制字符串

    return md5_hex

class KnowledgeBaseService(object):
    def __init__(self):
        #如果文件夹不存在则创建，如果存在则跳过
        os.makedirs(config.persist_directory, exist_ok=True)

        self.chroma = Chroma(
            collection_name=config.collection_name,   #向量库名称
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory
        ) #向量存储的实例 Chroma向量库对象

        self.split = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,       #分割后的文本段最大长度
            chunk_overlap=config.chunk_overlap, #连续文本段之间的字符重叠数量
            separators=config.separators,       #自然段落划分的符号
            length_function=len,
        )#文本分割器的对象


    def upload_by_str(self,data,filename):
        """将传入的字符串进行向量化，存入向量数据库中"""
        #先得到传入字符串的md5值
        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):                  #判断内容是否重复
            return "[跳过]内容已经存在知识库中"

        if len(data) > config.max_split_char_number:
            knowledge_chunks: list[str] = self.split.split_text(data)
        else:
            knowledge_chunks = [data]

        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "lsj"
        }

        self.chroma.add_texts(      #内容加载到向量库中
            texts=knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks]
        )

        save_md5(md5_hex)
        return "[完成]内容已经保存到知识库中"


"""
知识库
"""
import os
from ollama import embeddings
from sqlalchemy.testing.suite.test_reflection import metadata
from sqlalchemy.util import md5_hex
from sympy.physics.units import length
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime


def check_md5(md5_str: str):
    """检查传入的 md5 函数是否已经被处理过了
        :return False(md5 未被处理过) True(已经处理过，已有记录)
    """
    if not os.path.exists(config.md5_path):
        # if 进入表示文件不存在
        open(config.md5_path, "w", encoding="utf-8").close()
        return False
    else:
        for line in open(config.md5_path, "r", encoding="utf-8").readlines():
            line = line.strip()  # 去掉换行符和空格
            if line == md5_str:
                return True  # 已经处理过
        return False


def save_md5(md5_str: str):
    """保存 md5 函数"""
    with open(config.md5_path, "a", encoding="utf-8") as f:
        f.write(md5_str + "\n")


def get_string_md5(input_str: str, encoding="utf-8"):
    """将传入的字符串转换为 md5 字符串"""

    str_bytes = input_str.encode(encoding=encoding)  # 将字符串转换为 bytes 字节数组
    md5_obj = hashlib.md5()  # 创建 md5 对象
    md5_obj.update(str_bytes)  # 更新内容 (传入即将要转换的字节数组)
    md5_hex = md5_obj.hexdigest()  # 得到 md5 的十六进制字符串

    return md5_hex


class KnowledgeBaseService(object):
    def __init__(self):
        # 如果文件夹不存在则创建，如果存在则跳过
        os.makedirs(config.persist_directory, exist_ok=True)

        self.chroma = Chroma(
            collection_name=config.collection_name,  # 向量库名称
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory
        )  # 向量存储的实例 Chroma 向量库对象

        self.split = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,  # 分割后的文本段最大长度
            chunk_overlap=config.chunk_overlap,  # 连续文本段之间的字符重叠数量
            separators=config.separators,  # 自然段落划分的符号
            length_function=len,
        )  # 文本分割器的对象

    def upload_by_str(self, data, filename):
        """将传入的字符串进行向量化，存入向量数据库中"""
        # 先得到传入字符串的 md5 值
        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):  # 判断内容是否重复
            return "[跳过] 内容已经存在知识库中"

        if len(data) > config.max_split_char_number:
            knowledge_chunks: list[str] = self.split.split_text(data)
        else:
            knowledge_chunks = [data]

        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "lsj"
        }

        self.chroma.add_texts(  # 内容加载到向量库中
            texts=knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks]
        )

        save_md5(md5_hex)
        return "[完成] 内容已经保存到知识库中"



