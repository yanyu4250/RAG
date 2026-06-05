import time
import streamlit as st
from dashscope.utils.oss_utils import upload_file
from knowledge_base import KnowledgeBaseService
"""
基于streamlit完成web网页的文档·  上传服务
"""
st.title("知识库更新服务")

#file_uploader,文件上传组件
uploader_file = st.file_uploader(
    "请上传TXT文件",
    type=["txt"],
    accept_multiple_files=False,    #False仅接受一个文件上传
)

service = KnowledgeBaseService()
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService ()

if uploader_file is not None:
    #提取文件的信息
    file_name = uploader_file.name
    file_size = uploader_file.size / 1024   #单位KB
    file_type = uploader_file.type

    st.subheader(f"文件名：{file_name}")
    st.write(f"文件格式：{file_type} | 大小：{file_size:.2f}KB")

    #获取文件内容 getvalue() --> bytes --> decode("utf-8")
    text = uploader_file.getvalue().decode("utf-8")

    with st.spinner("载入知识库中。。。"):   #在spinner中的代码执行过程中会有一个加载动画
        time.sleep(1)
        result = st.session_state["service"].upload_by_str(text,file_name)
        st.write(result)

