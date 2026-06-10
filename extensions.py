import streamlit as st
import datetime
import json

# 适配原有排版风格：功能函数+注释规范
def export_chat_history(messages):
    """
    导出对话记录为JSON格式
    :param messages: 会话状态中的messages列表（与app.py格式一致）
    :return: 格式化的JSON字符串、下载文件名
    """
    # 整理对话记录（保持原有角色命名：孩子/AI老师）
    formatted_chat = []
    for msg in messages:
        role = "孩子" if msg["role"] == "user" else "AI老师"
        formatted_chat.append({
            "角色": role,
            "内容": msg["content"],
            "时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # 生成带时间戳的文件名，适配儿童课堂场景
    filename = f"小小思想家_对话记录_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    # 格式化JSON，方便阅读
    json_chat = json.dumps(formatted_chat, ensure_ascii=False, indent=2)
    
    return json_chat, filename

def show_chat_export_ui():
    """
    渲染导出功能的UI（适配原有侧边栏排版风格）
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("第四步：对话记录管理")
    
    # 按钮风格与原有一致（清空、生成报告按钮同样式）
    if st.sidebar.button("📤 导出对话记录"):
        if len(st.session_state.messages) < 2:
            st.sidebar.warning("暂无有效对话记录可导出～")
        else:
            chat_json, filename = export_chat_history(st.session_state.messages)
            # 下载按钮适配Streamlit宽布局，与原有界面风格统一
            st.sidebar.download_button(
                label="点击下载JSON文件",
                data=chat_json,
                file_name=filename,
                mime="application/json",
                use_container_width=True  # 适配原有wide布局
            )
            st.sidebar.success("记录已准备好，点击按钮即可下载～")