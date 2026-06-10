import streamlit as st
import streamlit.components.v1 as components

def voice_toggle():
    """聊天输入框旁的语音/键盘切换按钮，识别后自动发送"""
    voice_html = """
    <div style="display: flex; align-items: center; height: 42px;">
        <button id="voiceToggleBtn" style="
            width: 40px; height: 40px; border-radius: 50%; border: none;
            background: #f0f2f6; cursor: pointer; display: flex; align-items: center; justify-content: center;
            transition: all 0.2s ease; font-size: 18px;
        " title="切换语音输入">
            📝
        </button>
    </div>

    <script>
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const btn = document.getElementById('voiceToggleBtn');
    let isListening = false;
    let recognition = null;

    function toggleButtonState(listening) {
        isListening = listening;
        btn.innerHTML = listening ? "🎤" : "📝";
        btn.style.background = listening ? "#4CAF50" : "#f0f2f6";
        btn.style.color = listening ? "white" : "inherit";
        btn.title = listening ? "正在聆听，点击停止" : "切换语音输入";
    }

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.interimResults = false;
        recognition.continuous = false;

        recognition.onresult = (e) => {
            const text = e.results[0][0].transcript;
            const chatInput = document.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (chatInput) {
                chatInput.value = text;
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                const enterEvent = new KeyboardEvent('keydown', {
                    key: 'Enter', code: 'Enter', keyCode: 13, which: 13,
                    bubbles: true, cancelable: true
                });
                chatInput.dispatchEvent(enterEvent);
            }
            toggleButtonState(false);
        };

        recognition.onend = () => toggleButtonState(false);
        recognition.onerror = () => toggleButtonState(false);

        btn.onclick = () => {
            if (!SpeechRecognition) {
                alert("当前浏览器不支持语音识别，请用Chrome/Edge");
                return;
            }
            if (!isListening) {
                toggleButtonState(true);
                recognition.start();
            } else {
                recognition.stop();
                toggleButtonState(false);
            }
        };
    } else {
        btn.title = "浏览器不支持语音识别";
        btn.style.opacity = "0.5";
    }
    </script>
    """
    components.html(voice_html, height=50)

