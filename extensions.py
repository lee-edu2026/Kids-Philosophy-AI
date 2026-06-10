import streamlit as st
import streamlit.components.v1 as components

def show_voice_input_toggle():  # 👈 这里改了函数名
    """聊天输入框旁的语音/键盘切换按钮，识别后自动发送"""
    # 嵌入带切换效果的语音按钮，和输入框无缝衔接
    voice_html = """
    <div style="display: flex; align-items: center; height: 42px;">
        <!-- 切换按钮：默认键盘图标，点击后变麦克风+聆听状态 -->
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

    // 按钮状态切换：键盘<->麦克风
    function toggleButtonState(listening) {
        isListening = listening;
        btn.innerHTML = listening ? "🎤" : "📝";
        btn.style.background = listening ? "#4CAF50" : "#f0f2f6";
        btn.style.color = listening ? "white" : "inherit";
        btn.title = listening ? "正在聆听，点击停止" : "切换语音输入";
    }

    // 初始化语音识别
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.interimResults = false;
        recognition.continuous = false;

        // 识别成功：填值+自动提交
        recognition.onresult = (e) => {
            const text = e.results[0][0].transcript;
            // 找到Streamlit自带的聊天输入框
            const chatInput = document.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (chatInput) {
                // 1. 把识别结果填入输入框
                chatInput.value = text;
                // 2. 触发输入事件，让Streamlit识别到内容变化
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                // 3. 模拟按回车，直接提交消息（和手动输入后按回车效果完全一致）
                const enterEvent = new KeyboardEvent('keydown', {
                    key: 'Enter', code: 'Enter', keyCode: 13, which: 13,
                    bubbles: true, cancelable: true
                });
                chatInput.dispatchEvent(enterEvent);
            }
            toggleButtonState(false); // 恢复按钮状态
        };

        // 识别结束/失败：恢复按钮状态
        recognition.onend = () => toggleButtonState(false);
        recognition.onerror = () => toggleButtonState(false);

        // 按钮点击逻辑：切换聆听状态
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
    # 嵌入按钮，高度和聊天输入框匹配
    components.html(voice_html, height=50)