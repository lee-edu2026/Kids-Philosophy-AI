import streamlit as st
import streamlit.components.v1 as components

def show_voice_input_for_chat():
    # 用侧边栏放语音按钮，不影响主界面排版
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎤 语音输入切换")

    voice_html = """
    <div style="margin: 10px 0;">
        <button id="voiceBtn" style="width:100%; padding:10px; font-size:16px; border-radius:8px; border:none; background:#4CAF50; color:white;">
            点击开始语音输入
        </button>
        <p id="voiceStatus" style="margin-top:8px; font-size:14px; color:#666;"></p>
    </div>

    <script>
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        document.getElementById('voiceStatus').innerText = "⚠️ 当前浏览器不支持语音识别，请用Chrome/Edge";
    } else {
        const recognition = new SpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.interimResults = false;
        recognition.continuous = false;

        const btn = document.getElementById('voiceBtn');
        const status = document.getElementById('voiceStatus');

        btn.onclick = () => {
            status.innerText = "🎙️ 正在聆听，请说话...";
            btn.disabled = true;
            recognition.start();
        };

        recognition.onresult = (e) => {
            const text = e.results[0][0].transcript;
            status.innerText = "✅ 识别完成：" + text;
            // 直接把结果填入页面底部的聊天输入框
            const chatInput = document.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (chatInput) {
                chatInput.value = text;
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            btn.disabled = false;
        };

        recognition.onerror = (e) => {
            status.innerText = "❌ 识别失败，请重试";
            btn.disabled = false;
        };

        recognition.onend = () => {
            btn.disabled = false;
            if (status.innerText.includes("正在聆听")) {
                status.innerText = "⌛ 未检测到语音，请重试";
            }
        };
    }
    </script>
    """
    components.html(voice_html, height=180)