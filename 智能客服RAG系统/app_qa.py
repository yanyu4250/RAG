import streamlit as st
import time
import os
import json
from datetime import datetime
from rag import RagService
from knowledge_base import KnowledgeBaseService
from file_history_store import FileChatMessageHistory

# 页面配置
st.set_page_config(
    page_title="智能客服系统",
    page_icon="🤖",
    layout="wide"
)

# 常量定义
CHAT_HISTORY_DIR = "./chat_history"
SESSION_METADATA_FILE = "./chat_history/session_metadata.json"

# 确保目录存在
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

# 标题和介绍
st.title("🤖 智能客服系统")
st.markdown("---")

# 初始化服务
if "rag_service" not in st.session_state:
    st.session_state.rag_service = RagService()

if "kb_service" not in st.session_state:
    st.session_state.kb_service = KnowledgeBaseService()

if "messages" not in st.session_state:
    st.session_state.messages = []


# 辅助函数：获取所有会话元数据
def get_all_sessions():
    """获取所有会话的元数据（session_id 和创建时间）"""
    if os.path.exists(SESSION_METADATA_FILE):
        with open(SESSION_METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# 辅助函数：保存会话元数据
def save_session_metadata(session_id, create_time=None):
    """保存或更新会话的元数据"""
    metadata = get_all_sessions()

    if session_id not in metadata:
        # 新会话，记录创建时间
        metadata[session_id] = {
            "create_time": create_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(SESSION_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    return metadata[session_id]["create_time"]


# 辅助函数：删除会话
def delete_session(session_id):
    """删除指定会话"""
    metadata = get_all_sessions()

    if session_id in metadata:
        del metadata[session_id]
        with open(SESSION_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    # 删除实际的会话文件
    session_file_path = os.path.join(CHAT_HISTORY_DIR, session_id)
    if os.path.exists(session_file_path):
        os.remove(session_file_path)


# 创建侧边栏
with st.sidebar:
    st.header("⚙️ 设置")

    # 会话 ID 管理
    if "session_id" not in st.session_state:
        st.session_state.session_id = "user_001"

    new_session_id = st.text_input(
        "会话 ID",
        value=st.session_state.session_id,
        help="用于区分不同用户的对话历史"
    )

    # 检测会话 ID 变化
    if new_session_id != st.session_state.session_id:
        st.session_state.session_id = new_session_id
        st.session_state.messages = []  # 切换会话时清空当前消息
        save_session_metadata(new_session_id)
        st.rerun()

    st.divider()

    # 历史会话列表
    st.subheader("📜 历史会话")

    all_sessions = get_all_sessions()

    if all_sessions:
        # 按创建时间倒序排序
        sorted_sessions = sorted(
            all_sessions.items(),
            key=lambda x: x[1]["create_time"],
            reverse=True
        )

        for session_id, meta in sorted_sessions:
            create_time = meta["create_time"]

            # 创建会话显示容器
            col1, col2 = st.columns([4, 1])

            with col1:
                # 显示会话 ID 和创建时间
                session_label = f"{session_id}"
                if st.button(
                        f"🗨️ {session_label}",
                        key=f"btn_{session_id}",
                        help=f"创建时间：{create_time}",
                        use_container_width=True
                ):
                    # 切换到该会话
                    st.session_state.session_id = session_id
                    st.session_state.messages = []
                    st.rerun()

            with col2:
                # 删除按钮
                if st.button("🗑️", key=f"del_{session_id}", help="删除此会话"):
                    delete_session(session_id)
                    if st.session_state.session_id == session_id:
                        st.session_state.session_id = "user_001"
                        st.session_state.messages = []
                    st.rerun()

        st.divider()

        # 新建会话按钮
        if st.button("➕ 新建会话", use_container_width=True):
            new_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            st.session_state.session_id = new_id
            st.session_state.messages = []
            save_session_metadata(new_id)
            st.rerun()
    else:
        st.info("暂无历史会话")
        st.divider()

        # 新建会话按钮
        if st.button("➕ 新建会话", use_container_width=True):
            new_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            st.session_state.session_id = new_id
            st.session_state.messages = []
            save_session_metadata(new_id)
            st.rerun()

    st.divider()

    # 知识库管理
    st.subheader("📚 知识库管理")

    uploaded_file = st.file_uploader(
        "上传知识文件",
        type=["txt"],
        help="支持 TXT 格式的文件上传"
    )

    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_size = uploaded_file.size / 1024

        st.info(f"📄 {file_name}\n📊 {file_size:.2f} KB")

        if st.button("添加到知识库"):
            try:
                text_content = uploaded_file.getvalue().decode("utf-8")

                with st.spinner("正在处理并添加到知识库..."):
                    result = st.session_state.kb_service.upload_by_str(
                        text_content,
                        file_name
                    )
                    st.success(result)

            except Exception as e:
                st.error(f"上传失败：{str(e)}")

    st.divider()

    # 清空当前会话历史
    if st.button("🗑️ 清空当前对话", use_container_width=True):
        # 清空文件中的历史记录
        history_file_path = os.path.join(CHAT_HISTORY_DIR, st.session_state.session_id)
        if os.path.exists(history_file_path):
            with open(history_file_path, "w", encoding="utf-8") as f:
                json.dump([], f)
        st.session_state.messages = []
        st.rerun()

# 主界面 - 聊天区域
st.subheader("💬 在线问答")

# 显示当前会话信息
current_session = st.session_state.session_id
all_sessions = get_all_sessions()
if current_session in all_sessions:
    create_time = all_sessions[current_session]["create_time"]
    st.caption(f"当前会话：{current_session} | 创建时间：{create_time}")

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入框
if prompt := st.chat_input("请输入您的问题..."):
    # 添加用户消息到状态
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)

    # 机器人回复
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                # 配置会话参数
                session_config = {
                    "configurable": {
                        "session_id": st.session_state.session_id
                    }
                }

                # 调用 RAG 服务获取回复
                response = st.session_state.rag_service.chain.invoke(
                    {"input": prompt},
                    session_config
                )

                # 显示回复
                st.markdown(response)

                # 添加助手消息到状态
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

                # 保存会话元数据（更新最后更新时间）
                save_session_metadata(st.session_state.session_id)

            except Exception as e:
                st.error(f"发生错误：{str(e)}")

# 页脚
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("Powered by LangChain & ChromaDB")
with col2:
    st.caption("Embedding: text-embedding-v4")
with col3:
    st.caption("Model: Qwen3-Max")
