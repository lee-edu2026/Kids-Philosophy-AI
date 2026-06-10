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
# --- 语音输入部分 ---
col1, col2 = st.columns([1, 10])
with col1:
    # 直接调用 speech_to_text 函数
    # 它会在界面上生成一个按钮，点击开始/停止录音
    # 识别到的文字会通过函数的返回值传回
    user_input_from_mic = speech_to_text(
        language='zh-CN',          # 设为中文
        start_prompt="🎙️ 录音",    # 按钮在未录音时的文字
        stop_prompt="⏹️ 停止",      # 按钮在录音中的文字
        just_once=True,            # 确保每次录音只返回一次结果
        use_container_width=True,  # 让按钮宽度自适应
        key="mic_recorder"         # 组件的唯一标识
    )
    
with col2:
    user_input_from_text = st.chat_input("在这里输入你的想法...")

# 统一处理输入（语音优先）
if user_input_from_mic and user_input_from_mic.strip():
    user_message = user_input_from_mic.strip()
elif user_input_from_text and user_input_from_text.strip():
    user_message = user_input_from_text.strip()
else:
    user_message = None

if user_message:
    # 原有展示和调用 API 的逻辑保持不变
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

