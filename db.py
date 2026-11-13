# db.py —— 只负责和 MySQL 打交道，不管聊天逻辑
import pymysql
import uuid

# ========= 这里改成你的 MySQL 信息 =========
DB_CONFIG = {
    "host": "localhost",      # 数据库所在电脑的地址，本机就是 localhost
    "port": 3306,             # MySQL 默认端口
    "user": "root",           # 用户名
    "password": "123456",    # ★★★ 改成你的 MySQL 密码 ★★★
    "charset": "utf8mb4",     # 支持中文和表情
}
DB_NAME = "kids_philosophy"   # 数据库名，会自动创建


def _connect(with_db=True):
    """打开一个数据库连接"""
    cfg = dict(DB_CONFIG)
    if with_db:
        cfg["database"] = DB_NAME
    return pymysql.connect(**cfg, autocommit=True)


def init_db():
    """第一次运行自动建库 + 建表（已存在就跳过，不会报错）"""
    # 1. 建库
    conn = _connect(with_db=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS {DB_NAME} "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        conn.close()

    # 2. 建表
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id     VARCHAR(36) PRIMARY KEY,
                    user_name      VARCHAR(50),
                    theme          VARCHAR(50),
                    start_question TEXT,
                    report         LONGTEXT,
                    status         VARCHAR(20) DEFAULT '进行中',
                    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(36),
                    role       VARCHAR(20),
                    content    LONGTEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_session (session_id),
                    FOREIGN KEY (session_id)
                        REFERENCES sessions(session_id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
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
