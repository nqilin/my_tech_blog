# Import core Flask class
from flask import Flask
# 新增：导入Flask默认的模板渲染函数（核心，用于加载HTML页面）
from flask import render_template
import sqlite3
import os


# Initialize Flask app
app = Flask(__name__)
# 保留Day2的secret_key（后续session要用，先写上）
app.secret_key = 'Vatey_tech_blog_2026'

# #################### SQLite Database Configuration ####################
# 数据库文件路径：项目根目录下的blog.db
DATABASE = os.path.join(app.root_path, 'blog.db')

# 连接数据库的通用函数（简化代码，避免重复编写）
def get_db_connection():
    # 连接SQLite数据库，返回连接对象
    conn = sqlite3.connect(DATABASE)
    # 设置查询结果以字典形式返回（默认是元组，字典更易操作）
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库：创建posts表 + 插入测试数据（仅首次运行执行）
def init_database():
    # 检查数据库文件是否存在，不存在则创建表+插数据
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        # 1. 执行SQL：创建posts文章表，字段和之前模拟数据完全一致
        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        # 2. 执行SQL：插入3篇测试文章（复用Day5的模拟数据）
        test_posts = [
            ('Getting Started with Flask Web Development', 'Python', 
             'Flask is a lightweight Python web framework that is perfect for beginners. This article records the basic steps of building a Flask project, including environment setup, route creation, and template rendering. We also learned how to use Jinja2 to pass data from backend to frontend and how to beautify pages with CSS.',
             '2026-02-04'),
            ('How to Use Git and GitHub for Version Control', 'Tools',
             'Git is an essential version control tool for developers. This article introduces the basic commands of Git, such as init, add, commit, pull and push. We also learned how to solve the push conflict problem and keep the commit history clean with rebase. GitHub is a great platform for hosting code and collaborating with others.',
             '2026-02-05'),
            ('HTML & CSS for Beginner Web Developers', 'Frontend',
             'HTML is the skeleton of web pages, and CSS is the skin. We learned how to build the basic structure of a web page with HTML, including header, nav, main and footer. We also used CSS to beautify the page, such as setting background color, box shadow, and hover effects. Flask uses url_for to import static resources like CSS correctly.',
             '2026-02-06')
        ]
        # 批量插入数据
        conn.executemany('INSERT INTO posts (title, category, content, date) VALUES (?, ?, ?, ?)', test_posts)
        # 提交事务+关闭连接（SQLite必须提交才会保存数据）
        conn.commit()
        conn.close()
        print("Database initialized successfully! Table 'posts' created and test data inserted.")

# 首次运行时初始化数据库
init_database()

# #################### Flask Routes (Query Data from SQLite) ####################
# 首页路由：从数据库查询所有文章，替代原模拟数据
@app.route('/')
def index():
    # 后端定义要传给前端的数据
    blog_data = {
        'title': 'Vatey Tech Blog',
        'subtitle': 'Share Technical Notes & Development Experiences',
        'latest_article_tip': 'Latest Technical Articles - Coming Soon!'
    }
    # 核心修改：从SQLite查询所有文章
    conn = get_db_connection()
    # 查询posts表中所有数据，按id倒序（最新的在最前面）
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close() # 关闭数据库连接，避免资源占用
    # 传递数据库查询结果给前端（前端无需修改，Jinja2语法完全兼容）
    return render_template('index.html', data=blog_data, posts=posts)

# 新增：博客关于页路由（核心多路由开发，和首页逻辑一致）
@app.route('/about')
def about():
    dev_data = {
        'title': 'About Me',
        'name': 'Chansopheavaty Houl (Lin)',
        'focus': 'Python & Web Development',
        'tech_stack': 'Python, Flask, SQLite, HTML/CSS/JavaScript'
    }
    # 渲染about.html，传dev_data给前端
    return render_template('about.html', dev=dev_data)

# 文章详情页路由：从数据库按ID查询单篇文章
@app.route('/article/<article_id>')
def article_detail(article_id):
    # 核心修改：从SQLite按id查询指定文章
    conn = get_db_connection()
    # 用?占位符防SQL注入，安全规范
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (article_id,)).fetchone()
    conn.close()
    # 传递数据库查询的单篇文章给前端（异常处理逻辑复用，404提示不变）
    return render_template('article.html', post=post)

# Run app in debug mode
if __name__ == '__main__':
    app.run(debug=True)