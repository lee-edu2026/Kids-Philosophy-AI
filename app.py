import streamlit as st
from openai import OpenAI
import prompts
import questions
import evaluator
from streamlit_mic_recorder import speech_to_text

# --- 1. 基础配置 ---
# 从 Streamlit 后台安全读取 Key
api_key = st.secrets["DEEPSEEK_API_KEY"]
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# --- 2. 界面设计 ---
st.set_page_config(page_title="小小思想家 AI 课堂", layout="wide")
st.title("🌟 小小思想家：儿童哲学 AI 课堂")

# 侧边栏：配置区
st.sidebar.header("课程配置")
theme_names = list(questions.QUESTION_BANK.keys())
selected_theme = st.sidebar.selectbox("第一步：选择今日探讨主题", theme_names)

# 获取当前主题对应的提示词和问题列表
current_system_prompt = {
    "自我与他人": prompts.TASK_1,
    "真善美": prompts.TASK_2,
    "自由与规则": prompts.TASK_3,
    "生命与自然": prompts.TASK_4
}[selected_theme]

# 侧边栏：问题选择
st.sidebar.markdown("---")
st.sidebar.subheader("第二步：由 AI 发起提问")
selected_q = st.sidebar.selectbox("从课本中挑选一个原问题：", ["请选择一个问题..."] + questions.QUESTION_BANK[selected_theme])

# 初始化对话记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 按钮：让 AI 自动问出选中的问题
if st.sidebar.button("开始教学（AI 提问）"):
    if selected_q != "请选择一个问题...":
        # 清空记录并让 AI 说出选中的原问题
        st.session_state.messages = [{"role": "assistant", "content": selected_q}]
        st.rerun()
    else:
        st.sidebar.warning("请先选一个问题呀！")

if st.sidebar.button("清空所有聊天"):
    st.session_state.messages = []
    st.rerun()

# --- 3. 对话展示区 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. 互动逻辑（语音+文本） ---
# 添加固定底部样式，将语音按钮和聊天输入框包裹在一起
st.markdown(
    """
    <style>
    .fixed-bottom-input {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: var(--secondary-background-color);
        padding: 0.5rem 1rem 0.8rem 1rem;
        z-index: 1000;
        width: 100%;
        border-top: 1px solid rgba(128, 128, 128, 0.2);
    }
    .stChatInput {
        background-color: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 用容器包裹语音按钮和文字输入框，并应用固定底部类
with st.container():
    st.markdown('<div class="fixed-bottom-input">', unsafe_allow_html=True)
    
    # 语音按钮（在上方）
    user_input_from_mic = speech_to_text(
        language='zh-CN',
        start_prompt="🎙️ 录音",
        stop_prompt="⏹️ 停止",
        just_once=True,
        use_container_width=True,
        key="mic_recorder"
    )
    
    # 文字输入框（在下方）
    user_input_from_text = st.chat_input("在这里输入你的想法...")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 统一处理输入（语音优先）
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
    
    # 发送消息后强制滚动到底部，避免新消息被固定栏遮挡
    st.rerun()

# --- 5. 评分报告 ---
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
