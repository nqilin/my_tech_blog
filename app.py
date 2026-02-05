# Import core Flask class
from flask import Flask
# 新增：导入Flask默认的模板渲染函数（核心，用于加载HTML页面）
from flask import render_template, request
# 顶部导入区域，添加这一行，导入数据库工具函数
from utils.db import get_db_connection, get_all_categories
# import sqlite3
import os



# Initialize Flask app
app = Flask(__name__)
# 保留Day2的secret_key（后续session要用，先写上）
app.secret_key = 'Vatey_tech_blog_2026'

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