import streamlit as st
from openai import OpenAI
import prompts
import questions
import evaluator
from streamlit_chat_widget import chat_input_widget
import speech_recognition as sr 
import io

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

# --- 4. 互动逻辑（修改为直接处理输入）---
# 不再需要 st.chat_input，直接使用新的组件
user_input = chat_input_widget()

# 用于存储最终的用户消息
final_user_message = None

# 检查组件是否有返回内容（无论是打字还是语音）
if user_input:
    # 情况1：用户输入的是文字
    if "text" in user_input:
        final_user_message = user_input["text"]
    
    # 情况2：用户输入的是语音（这是本次修改的核心）
    elif "audioFile" in user_input:
        # 获取音频数据（bytes）
        audio_bytes = bytes(user_input["audioFile"])
        # 使用临时缓冲区处理音频数据
        with io.BytesIO(audio_bytes) as audio_file:
            # 加载音频数据
            r = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio_data = r.record(source)
            # 调用 Google 免费语音识别，将音频转为中文文本
            try:
                final_user_message = r.recognize_google(audio_data, language="zh-CN")
            except sr.UnknownValueError:
                st.warning("抱歉，没能听清楚，可以再说一遍吗？")
            except sr.RequestError:
                st.warning("语音服务请求失败，请检查网络。")
    
    # 如果成功得到了用户消息（无论是打字还是语音），就发送给AI
    if final_user_message:
        # 将用户消息保存到聊天记录并显示
        st.session_state.messages.append({"role": "user", "content": final_user_message})
        with st.chat_message("user"):
            st.markdown(final_user_message)

        # 调用 DeepSeek API 获取回复
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

