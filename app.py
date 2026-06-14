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

# --- 3. 对话展示区 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. 互动逻辑（语音+文本）—— 完全自定义固定栏 ---

# 先加上修复 transform 的 CSS（这是关键）
st.markdown(
    """
    <style>
    /* 修复 Streamlit 的 transform 导致 fixed 失效的问题 */
    .stApp {
        transform: none !important;
    }
    /* 固定底部栏样式 */
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
        display: flex;
        gap: 8px;
        align-items: center;
    }
    /* 让文本输入框自动撑满剩余宽度 */
    .fixed-bottom-input .stTextInput {
        flex: 1;
        margin-bottom: 0;
    }
    /* 给聊天记录底部留出空间 */
    .main .block-container {
        padding-bottom: 100px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 这里不再用 st.chat_input，改用普通文本输入框
# 先用一个容器占位，让固定栏出现在最后
with st.container():
    st.markdown('<div class="fixed-bottom-input">', unsafe_allow_html=True)
    
    # 语音按钮（宽度自动）
    user_input_from_mic = speech_to_text(
        language='zh-CN',
        start_prompt="🎙️",
        stop_prompt="⏹️",
        just_once=True,
        use_container_width=False,
        key="mic_recorder"
    )
    
    # 文本输入框（用 st.text_input 模拟聊天输入）
    user_input_from_text = st.text_input(
        "在这里输入你的想法...",
        value=st.session_state.get("text_input", ""),
        key="text_input",
        label_visibility="collapsed",
        placeholder="按回车发送..."
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# 处理输入（语音优先）
user_message = None
if user_input_from_mic and user_input_from_mic.strip():
    user_message = user_input_from_mic.strip()
elif user_input_from_text and user_input_from_text.strip():
    user_message = user_input_from_text.strip()

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
