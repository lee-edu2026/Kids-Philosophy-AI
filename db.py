# db.py —— 专门负责和 PostgreSQL 打交道
import psycopg2
import uuid
import streamlit as st

# 从 Streamlit Secrets 读取数据库配置
DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "port": int(st.secrets["DB_PORT"]),
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "dbname": st.secrets["DB_NAME"],
    "sslmode": "require"
}

def _connect():
    """打开一个数据库连接（并开启自动提交）"""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn

def init_db():
    """建表（已存在就跳过，不会报错）"""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id     VARCHAR(36) PRIMARY KEY,
                    user_name      VARCHAR(50),
                    theme          VARCHAR(50),
                    start_question TEXT,
                    report         TEXT,
                    status         VARCHAR(20) DEFAULT '进行中',
                    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id         SERIAL PRIMARY KEY,
                    session_id VARCHAR(36) REFERENCES sessions(session_id) ON DELETE CASCADE,
                    role       VARCHAR(20),
                    content    TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    finally:
        conn.close()

def create_session(user_name, theme, start_question):
    """新建一节课，返回这节课的唯一编号"""
    sid = str(uuid.uuid4())
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sessions (session_id, user_name, theme, start_question) "
                "VALUES (%s, %s, %s, %s)",
                (sid, user_name, theme, start_question),
            )
    finally:
        conn.close()
    return sid

def save_message(session_id, role, content):
    """存一条对话（role 是 user 或 assistant）"""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
                (session_id, role, content),
            )
    finally:
        conn.close()

def save_report(session_id, report):
    """把评估报告写进这节课，并把状态改为已结束"""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE sessions SET report=%s, status='已结束' WHERE session_id=%s",
                (report, session_id),
            )
    finally:
        conn.close()

# ================= 下面是读取历史记录的函数 =================

def get_all_sessions():
    """获取所有历史课程（按时间倒序）"""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT session_id, user_name, theme, status, 
                       to_char(created_at, 'YYYY-MM-DD HH24:MI')
                FROM sessions 
                ORDER BY created_at DESC
            """)
            return cur.fetchall()
    finally:
        conn.close()

def get_messages_by_session(session_id):
    """获取某节课的完整对话"""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT role, content FROM messages 
                WHERE session_id = %s ORDER BY id ASC
            """, (session_id,))
            return cur.fetchall()
    finally:
        conn.close()

def get_report_by_session(session_id):
    """获取某节课的报告"""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT report FROM sessions WHERE session_id = %s", (session_id,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        conn.close()
