import streamlit as st

#设置页面配置
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://streamlit.io/',
        'Report a bug': "https://streamlit.io/",
        'About': "这是一个AI智能伴侣！"
    }
)

#大标题
st.title("stream入门演示")
st.header("stream一级标题")
st.subheader("stream二级标题")