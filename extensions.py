import streamlit as st
import streamlit.components.v1 as components

def voice_toggle():
    voice_html = """
    <div style="display: flex; align-items: center; height: 42px;">
        <button id="voiceToggleBtn" style="width:40px;height:40px;border-radius:50%;border:none;background:#f0f2f6;cursor:pointer;">🎤</button>
    </div>
    <script>
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const btn = document.getElementById('voiceToggleBtn');
    let recognition = null;
    let listening = false;

    function toggleUI(isListening) {
        listening = isListening;
        btn.innerHTML = isListening ? "🔴" : "🎤";
        btn.style.background = isListening ? "#ff4444" : "#f0f2f6";
    }

    function fillChatInput(text) {
        // 多种选择器尝试
        const selectors = [
            'div[data-testid="stChatInput"] textarea',
            'textarea[data-testid="stChatInputTextArea"]',
            'div[data-testid="stChatInput"] input',
            '.stChatInput textarea'
        ];
        let textarea = null;
        for (let sel of selectors) {
            textarea = document.querySelector(sel);
            if (textarea) break;
        }
        
        if (textarea) {
            textarea.value = text;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            // 不自动发送，让用户手动按回车或点击发送按钮
        } else {
            alert("找不到聊天输入框，请刷新页面重试");
        }
    }

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.interimResults = false;
        recognition.continuous = false;

        recognition.onresult = (e) => {
            const text = e.results[0][0].transcript;
            fillChatInput(text);
            toggleUI(false);
        };
        recognition.onerror = (e) => {
            console.error(e);
            alert("语音识别出错，请检查麦克风权限");
            toggleUI(false);
        };
        recognition.onend = () => toggleUI(false);

        btn.onclick = () => {
            if (!listening) {
                try {
                    recognition.start();
                    toggleUI(true);
                } catch(e) {
                    alert("无法启动语音识别，请刷新页面重试");
                }
            } else {
                recognition.stop();
                toggleUI(false);
            }
        };
    } else {
        btn.title = "当前浏览器不支持语音识别";
        btn.style.opacity = "0.5";
        btn.onclick = () => alert("请使用 Chrome 或 Edge 浏览器，并确保 HTTPS 或 localhost 访问");
    }
    </script>
    """
    components.html(voice_html, height=50)
