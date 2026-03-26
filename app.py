import streamlit as st
from openai import OpenAI

# --- 1. 基础配置 (后续可替换打分逻辑) --- [cite: 7]
api_key = st.secrets[
"DEEPSEEK_API_KEY"
]
client = OpenAI(api_key=api_key, base_url=
"https://api.deepseek.com"
)

# --- 2. 高级提示词预设 --- [cite: 6]
SYSTEM_PROMPT = """你是一位温柔、有耐心的儿童哲学引导员。
你的任务是引导7-10岁孩子进行哲学思考。
要求：
1. 语言平实、充满童趣，多用比喻。
2. 采用苏格拉底式提问，不要直接给答案，而是通过追问引导孩子思考。
3. 鼓励孩子表达，无论答案对错都先给予情感肯定。
4. 每次对话结束前，都要针对当前主题抛出一个引导性问题。"""

# --- 3. 界面设计 ---
st.title("🌟 小小思想家：儿童哲学 AI 课堂")
scene = st.sidebar.selectbox("选择今日课程主题：", ["认识AI", "学会提问", "真假之辩", "人与机器"]) # [cite: 8]

if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. 对话逻辑 ---
if prompt := st.chat_input("和 AI 老师聊聊你的想法吧..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 这里的 prompt 结合了主题场景
        full_prompt = f"当前主题是【{scene}】。用户说：{prompt}"
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *st.session_state.messages
            ],
            stream=False
        )
        answer = response.choices[0].message.content
        st.markdown(answer)
        
    st.session_state.messages.append({"role": "assistant", "content": answer})

# --- 5. 打分功能预留区 (后续替换代码文件即可) --- [cite: 3, 5, 7]
if st.sidebar.button("生成哲学思维报告"):
    st.sidebar.info("打分模块已就绪，等待后续标准导入...")