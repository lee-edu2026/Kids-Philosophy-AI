import streamlit as st
from openai import OpenAI
import prompts

# --- 1. 基础配置 ---
# 从 Streamlit 后台安全读取 Key [cite: 15]
api_key = st.secrets["DEEPSEEK_API_KEY"]
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# --- 2. 四大主题高级提示词库  --- 
PROMPTS_BANK = {
    "认识AI": prompts.TASK_1,
    "学会提问": prompts.TASK_2,
    "真假之辩": prompts.TASK_3,
    "人与机器": prompts.TASK_4
}

# --- 3. 界面设计 --- [cite: 10]
st.title("🌟 小小思想家：儿童哲学 AI 课堂")

# 在左侧选择主题 
scene = st.sidebar.selectbox("选择今日课程主题：", list(PROMPTS_BANK.keys()))

# 这里的“重置对话”按钮很有用，切换主题时可以清空之前的聊天记录
if st.sidebar.button("开启新讨论（清空记录）"):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. 对话逻辑 --- [cite: 3]
if prompt := st.chat_input("和 AI 老师聊聊你的想法吧..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 自动根据选择的主题获取对应的提示词 
        current_system_prompt = PROMPTS_BANK[scene]
        
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

# --- 5. 打分功能预留区 --- [cite: 5, 7]
st.sidebar.markdown("---")
if st.sidebar.button("生成哲学思维报告"):
    st.sidebar.info("打分模块已就绪，等待后续标准导入...")