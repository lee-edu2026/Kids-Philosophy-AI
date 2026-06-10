import streamlit as st
from openai import OpenAI
import prompts
import questions
import evaluator
from streamlit_mic_recorder import speech_to_text

# --- 1. 基础配置 ---
api_key = st.secrets["DEEPSEEK_API_KEY"]
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# --- 2. 界面设计 ---
st.set_page_config(page_title="小小思想家 AI 课堂", layout="wide")
st.title("🌟 小小思想家：儿童哲学 AI 课堂")

# 侧边栏配置 (保持不变)
st.sidebar.header("课程配置")
theme_names = list(questions.QUESTION_BANK.keys())
selected_theme = st.sidebar.selectbox("第一步：选择今日探讨主题", theme_names)

current_system_prompt = {
    "自我与他人": prompts.TASK_1,
    "真善美": prompts.TASK_2,
    "自由与规则": prompts.TASK_3,
    "生命与自然": prompts.TASK_4
}[selected_theme]

st.sidebar.markdown("---")
st.sidebar.subheader("第二步：由 AI 发起提问")
selected_q = st.sidebar.selectbox("从课本中挑选一个原问题：", ["请选择一个问题..."] + questions.QUESTION_BANK[selected_theme])

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.button("开始教学（AI 提问）"):
    if selected_q != "请选择一个问题...":
        st.session_state.messages = [{"role": "assistant", "content": selected_q}]
        st.rerun()
    else:
        st.sidebar.warning("请先选一个问题呀！")

if st.sidebar.button("清空所有聊天"):
    st.session_state.messages = []
    st.rerun()

# 添加CSS，为消息区域预留底部内边距，防止被固定栏遮挡
st.markdown(
    """
    <style>
    /* 调整主内容区底部内边距，为工具栏留出空间 */
    .main .block-container {
        padding-bottom: 150px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. 对话展示区 (保持不变)---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. 使用官方 st.bottom 容器修复底部固定问题 ---
# 使用官方 st.bottom 容器，确保输入区域始终固定在页面底部
with st.bottom():
    # 语音按钮 (来自 streamlit_mic_recorder)
    user_input_from_mic = speech_to_text(
        language='zh-CN',
        start_prompt="🎙️ 录音",
        stop_prompt="⏹️ 停止",
        just_once=True,
        use_container_width=True,
        key="mic_recorder"
    )

    # 聊天输入框 (streamlit 原生)
    user_input_from_text = st.chat_input("在这里输入你的想法...")

# 统一处理输入 (逻辑保持不变)
if user_input_from_mic and user_input_from_mic.strip():
    user_message = user_input_from_mic.strip()
elif user_input_from_text and user_input_from_text.strip():
    user_message = user_input_from_text.strip()
else:
    user_message = None

if user_message:
    st.session_state.messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": current_system_prompt},
                *st.session_state.messages
            ],
            stream=False
        )
        answer = response.choices[0].message.content
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        # 在生成回答后让页面滚动到底部，以获得流畅的聊天体验
        st.rerun()

# --- 5. 评分报告 (保持不变)---
st.sidebar.markdown("---")
st.sidebar.subheader("第三步：结课评估")
if st.sidebar.button("生成哲学思维报告"):
    if len(st.session_state.messages) < 2:
        st.sidebar.warning("对话还未开始，无法生成报告。")
    else:
        with st.sidebar.expander("📝 哲学思维分析报告", expanded=True):
            with st.spinner("专家正在分析中..."):
                report = evaluator.get_report(client, st.session_state.messages)
                st.markdown(report)
