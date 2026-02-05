# Import core Flask class
from flask import Flask
# 新增：导入Flask默认的模板渲染函数（核心，用于加载HTML页面）
from flask import render_template, request
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

# 【新增核心函数】查询数据库中所有唯一分类（去重），供所有页面渲染动态分类
def get_all_categories():
    conn = get_db_connection()
    # 查唯一分类并按名称排序，DISTINCT是去重关键字
    categories = conn.execute('SELECT DISTINCT category FROM posts ORDER BY category').fetchall()
    conn.close()
    # 把sqlite3.Row对象转成纯字符串列表，方便前端渲染
    return [cat['category'] for cat in categories]

# 首次运行时初始化数据库
init_database()

# #################### 通用数据：复用所有页面的blog_data ####################
# 【新增】抽离首页的blog_data，供详情页/分类页复用，避免重复代码
BLOG_GLOBAL_DATA = {
    'title': 'Vatey Tech Blog',
    'subtitle': 'Share Technical Notes & Development Experiences',
    'latest_article_tip': 'Latest Technical Articles'
}

# #################### Flask Routes (Query Data from SQLite) ####################
# 首页路由：从数据库查询所有文章，替代原模拟数据
@app.route('/')
def index():
    # 接收搜索框的query参数（GET请求，无搜索时为None）
    search_query = request.args.get('query', '').strip()

     # 查所有文章
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    
    # 根据是否有搜索词执行不同查询
    if search_query:
        # 核心：模糊查询（标题或正文包含搜索词），防SQL注入
        posts = conn.execute('''
            SELECT * FROM posts 
            WHERE title LIKE ? OR content LIKE ? 
            ORDER BY id DESC
        ''', (f'%{search_query}%', f'%{search_query}%')).fetchall()  # %通配符匹配任意字符
    else:
        # 无搜索词时，默认显示所有文章
        posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    # 传递：全局data + 分类 + 文章
    return render_template(
        'index.html',
        data=BLOG_GLOBAL_DATA,
        categories=get_all_categories(),
        posts=posts,
        search_query=search_query  # 传递搜索词回显到搜索框
    )

# 新增：博客关于页路由（核心多路由开发，和首页逻辑一致）
@app.route('/about')
def about():
    dev_data = {
        'title': 'About Me',
        'name': 'Chansopheavaty Houl (Lin)',
        'focus': 'Python & Web Development',
        'tech_stack': 'Python, Flask, SQLite, HTML/CSS/JavaScript'
    }
    # 新增传递categories，解决关于页分类渲染错误
    return render_template(
        'about.html',
        data=BLOG_GLOBAL_DATA,
        dev=dev_data,
        categories=get_all_categories()
    )

# 文章详情页路由：从数据库按ID查询单篇文章
@app.route('/article/<article_id>')
def article_detail(article_id):
    # 核心修改：从SQLite按id查询指定文章
    conn = get_db_connection()
    # 用?占位符防SQL注入，安全规范
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (article_id,)).fetchone()
    conn.close()
    # 新增传递：全局data + 分类，彻底解决'data'和'categories'未定义错误
    return render_template(
        'article.html',
        data=BLOG_GLOBAL_DATA,  # 补充data参数
        categories=get_all_categories(),  # 补充categories参数
        post=post  # 原有post参数保留
    )

# 分类筛选路由：新增「分类+搜索」叠加功能（双条件筛选）
@app.route('/category/<category_name>')
def category_posts(category_name):
    # 1. 接收搜索框的query参数（和首页搜索一致，无搜索则为空）
    search_query = request.args.get('query', '').strip()

    # 2. 连接数据库，根据「分类+是否有搜索词」执行双条件查询
    conn = get_db_connection()
    if search_query:
        # 叠加查询：分类匹配 + 标题/正文包含搜索词（双条件）
        posts = conn.execute('''
            SELECT * FROM posts 
            WHERE category = ? AND (title LIKE ? OR content LIKE ?)
            ORDER BY id DESC
        ''', (category_name, f'%{search_query}%', f'%{search_query}%')).fetchall()
    else:
        # 纯分类查询：仅匹配分类
        posts = conn.execute(
            'SELECT * FROM posts WHERE category = ? ORDER BY id DESC',
            (category_name,)
        ).fetchall()
    conn.close()

    # 3. 渲染模板，传递「搜索词」（回显到搜索框+页面标题）
    return render_template(
        'category.html',
        data=BLOG_GLOBAL_DATA,
        categories=get_all_categories(),
        category_name=category_name,
        posts=posts,
        search_query=search_query  # 新增：传递搜索词，实现搜索框回显
    )

# Run app in debug mode
if __name__ == '__main__':
    app.run(debug=True)