# db.py —— 专门负责和 PostgreSQL 打交道
import psycopg2
import uuid

# ========= 这里已经填好了你截图里的 Aiven 信息 =========
DB_CONFIG = {
    "host": "pg-1c32e431-project-0000.j.aivencloud.com",
    "port": 12482,
    "user": "avnadmin",
    "password": st.secrets["DB_PASSWORD"],  # ★★★ 如果稍后重置了密码，记得改这里 ★★★
    "dbname": "defaultdb",                   # Aiven 默认的数据库名
    "sslmode": "require"                     # Aiven 强制要求使用 SSL 加密连接
}


def _connect():
    """打开一个数据库连接（并开启自动提交）"""
    # psycopg2 默认不是自动提交的，我们要设成自动提交，省去手动 commit 的麻烦
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn


def init_db():
    """建表（已存在就跳过，不会报错）"""
    # 注意：PostgreSQL 的建表语法和 MySQL 略有不同，比如主键用 SERIAL，文本用 TEXT
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
