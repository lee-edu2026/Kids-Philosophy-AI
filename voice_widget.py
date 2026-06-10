# voice_widget.py
import streamlit as st
from streamlit.components.v1 import html

def voice_input_button(key: str = "default_voice"):
    """
    创建一个语音输入按钮组件。
    返回识别到的文本，如果没有识别则返回 None。
    """
    component_html = f"""
    <div id="root-{key}"></div>
    <script>
    (function() {{
        const container = document.getElementById('root-{key}');
        if (!container) return;

        // 创建按钮
        const btn = document.createElement('button');
        btn.innerHTML = '🎙️';
        btn.style.fontSize = '24px';
        btn.style.padding = '8px 16px';
        btn.style.borderRadius = '8px';
        btn.style.border = '1px solid #ccc';
        btn.style.cursor = 'pointer';
        btn.style.backgroundColor = '#f0f2f6';
        container.appendChild(btn);

        // Web Speech API 设置
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {{
            btn.disabled = true;
            btn.title = '浏览器不支持语音识别';
            return;
        }}

        const recognition = new SpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        let isListening = false;

        btn.onclick = () => {{
            if (isListening) {{
                recognition.stop();
                return;
            }}
            isListening = true;
            btn.innerHTML = '🔴 录音中...';
            btn.style.backgroundColor = '#ffcccc';
            recognition.start();
        }};

        recognition.onresult = (event) => {{
            const transcript = event.results[0][0].transcript;
            isListening = false;
            btn.innerHTML = '🎙️';
            btn.style.backgroundColor = '#f0f2f6';
            // 将识别的文本发送回 Streamlit
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: transcript,
            }}, '*');
        }};

        recognition.onerror = (event) => {{
            isListening = false;
            btn.innerHTML = '🎙️';
            btn.style.backgroundColor = '#f0f2f6';
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: null,
            }}, '*');
        }};

        recognition.onend = () => {{
            if (isListening) {{
                isListening = false;
                btn.innerHTML = '🎙️';
                btn.style.backgroundColor = '#f0f2f6';
            }}
        }};
    }})();
    </script>
    """
    # 使用 components.html 嵌入，并通过 key 参数获取返回值
    value = html(component_html, height=70, key=f"voice_comp_{key}")
    return value
