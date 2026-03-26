# 这里是根据《儿童哲学思考评分细则表》编写的逻辑 
EVAL_PROMPT_TEMPLATE = """
你现在是一名专业的儿童哲学教育评估专家。请根据以下对话记录，参考《评分细则表》对孩子的表现进行打分。

### 评分维度与细则[cite: 19, 20]:
1. 概念理解：0(无法理解) -> 3(深度抽象/多角度阐释) [cite: 23]
2. 理由支持：0(无理由) -> 3(多层次/反驳性理由) [cite: 26]
3. 矛盾意识：0(无意识) -> 3(主动修正/逻辑缜密) [cite: 29]
4. 追问能力：0(无追问) -> 3(连环追问/反思性) [cite: 32]
5. 观点原创性：0(无原创) -> 3(高度原创/独特比喻) [cite: 35]

### 待评估的对话记录:
{chat_history}

### 输出要求:
请给出每个维度的得分（0-3分）及简短的理由，最后给出一个总分和一段温柔的鼓励建议。
"""

def get_report(client, messages):
    # 将对话记录整理成文字
    chat_text = ""
    for m in messages:
        role = "孩子" if m["role"] == "user" else "AI老师"
        chat_text += f"{role}: {m['content']}\n"
    
    # 调用 AI 进行分析
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一位客观严谨且充满爱心的哲学评估专家。"},
            {"role": "user", "content": EVAL_PROMPT_TEMPLATE.format(chat_history=chat_text)}
        ]
    )
    return response.choices[0].message.content