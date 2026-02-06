# utils/db.py 数据库函数迁移解耦
# 导入需要的模块
import sqlite3
import os
from flask import Flask

# 初始化Flask实例
app = Flask(__name__)
app.secret_key = 'Vatey_tech_blog_2026' 

# 数据库文件路径：项目根目录下的blog.db
DATABASE = os.path.join(app.root_path, 'blog.db')

# 1. 连接数据库的通用函数
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 字典形式返回结果
    return conn

# 2. 初始化数据库：创建posts表 + 插入测试数据
def init_database():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        # 创建posts表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                date DATE NOT NULL     
            )
        ''')
        # 插入3篇测试文章
        # test_posts = [
        #     ('Getting Started with Flask Web Development', 'Python', 
        #      'Flask is a lightweight Python web framework that is perfect for beginners. This article records the basic steps of building a Flask project, including environment setup, route creation, and template rendering. We also learned how to use Jinja2 to pass data from backend to frontend and how to beautify pages with CSS.',
        #      '2026-02-04'),
        #     ('How to Use Git and GitHub for Version Control', 'Tools',
        #      'Git is an essential version control tool for developers. This article introduces the basic commands of Git, such as init, add, commit, pull and push. We also learned how to solve the push conflict problem and keep the commit history clean with rebase. GitHub is a great platform for hosting code and collaborating with others.',
        #      '2026-02-05'),
        #     ('HTML & CSS for Beginner Web Developers', 'Frontend',
        #      'HTML is the skeleton of web pages, and CSS is the skin. We learned how to build the basic structure of a web page with HTML, including header, nav, main and footer. We also used CSS to beautify the page, such as setting background color, box shadow, and hover effects. Flask uses url_for to import static resources like CSS correctly.',
        #      '2026-02-06')
        # ]
        # conn.executemany('INSERT INTO posts (title, category, content, date) VALUES (?, ?, ?, ?)', test_posts)
        conn.commit()
        conn.close()
        print("Database initialized successfully! Table 'posts' created and test data inserted.")

# 3. 查询所有唯一分类（去重，返回纯字符串列表）
def get_all_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT DISTINCT category FROM posts ORDER BY category').fetchall()
    conn.close()
    return [cat['category'] for cat in categories]

# 执行数据库初始化
init_database()