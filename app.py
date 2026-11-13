import streamlit as st
from openai import OpenAI
import prompts
import questions
import evaluator
from streamlit_mic_recorder import speech_to_text
import db

# --- 1. 基础配置 ---
api_key = st.secrets["DEEPSEEK_API_KEY"]
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# --- 数据库初始化（只跑一次，失败也不影响聊天）---
try:
    if not st.session_state.get("db_inited"):
        db.init_db()
        st.session_state.db_inited = True
except Exception as e:
    st.sidebar.warning(f"⚠️ 数据库未连接：{e}（聊天功能不受影响）")

# --- 2. 界面设计 ---
st.set_page_config(page_title="小小思想家 AI 课堂", layout="wide")
st.title("🌟 小小思想家：儿童哲学 AI 课堂")

st.sidebar.header("课程配置")
user_name = st.sidebar.text_input("你的名字：", value="小朋友")
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
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if st.sidebar.button("开始教学（AI 提问）"):
    if selected_q != "请选择一个问题...":
        st.session_state.messages = [{"role": "assistant", "content": selected_q}]
        # ---- 存数据库：新建一节课 + 存下第一句 AI 提问 ----
        try:
            sid = db.create_session(user_name, selected_theme, selected_q)
            db.save_message(sid, "assistant", selected_q)
            st.session_state.session_id = sid
        except Exception as e:
            st.sidebar.warning(f"⚠️ 保存失败：{e}")
        st.rerun()
    else:
        st.sidebar.warning("请先选一个问题呀！")

if st.sidebar.button("清空所有聊天（开启新话题）"):
    st.session_state.messages = []
    st.session_state.session_id = None   # 只清内存，数据库旧记录保留
    st.rerun()

# --- 3. 对话展示区 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. 互动逻辑（语音+文本） ---

# 固定底部容器：语音按钮在上，文字输入框在下
col1, col2 = st.columns([6, 1])
with col2:
    user_input_from_mic = speech_to_text(
        language='zh-CN',
        start_prompt="🎙️语音输入",
        stop_prompt="⏹️停止说话",
        just_once=True,
        use_container_width=True,
        key="mic_recorder"
    )

# 文本输入框（这个会自动固定在底部）
user_input_from_text = st.chat_input("在这里输入你的想法...")

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
                # ---- 存数据库：用户这条 + AI 这条 ----
        try:
            if st.session_state.session_id:
                db.save_message(st.session_state.session_id, "user", user_message)
                db.save_message(st.session_state.session_id, "assistant", answer)
        except Exception as e:
            st.warning(f"⚠️ 对话保存失败：{e}")
    
    
    
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
                                # ---- 存数据库：报告写进这节课，状态改为已结束 ----
                try:
                    if st.session_state.session_id:
                        db.save_report(st.session_state.session_id, report)
                except Exception as e:
                    st.warning(f"⚠️ 报告保存失败：{e}")
