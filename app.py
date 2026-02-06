# Import core Flask class
from flask import Flask
# 新增：导入Flask默认的模板渲染函数（核心，用于加载HTML页面）
from flask import render_template, request, jsonify, session, flash, redirect, url_for
# 顶部导入区域，添加这一行，导入数据库工具函数
from utils.db import get_db_connection, get_all_categories
from datetime import datetime
import os



# Initialize Flask app
app = Flask(__name__)
# 保留Day2的secret_key（后续session要用，先写上）
app.secret_key = 'Vatey_tech_blog_2026'

# #################### 登录验证 ####################
# 1. 硬编码管理员账号密码（后续接数据库仅需修改这里）
ADMIN_USER = "admin"       # 可自定义，比如你的用户名
ADMIN_PWD = "123456"       # 可自定义，测试用简单密码即可

# 2. 后台权限控制装饰器：未登录用户访问后台，自动跳登录页
def admin_required(f):
    """权限装饰器：检查session中的登录状态，未登录则拦截"""
    def wrapper(*args, **kwargs):
        # 仅当session中有「is_login」且为True时，才允许访问后台
        if not session.get("is_login"):
            return redirect(url_for("admin_login"))  # 跳转到登录路由（admin_login）
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__  # 修复Flask路由名称冲突，必须加
    return wrapper

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

# #################### Admin Routes (Page Only) ####################
# 后台登录页
@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    # 防止重复登录：已登录用户访问登录页，直接跳后台首页
    if session.get("is_login"):
        return redirect(url_for("admin_dashboard"))
    
    # POST请求：前端提交账号密码，执行验证
    if request.method == "POST":
        # 获取前端表单的用户名/密码，去除首尾空格（防用户误输）
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        # 验证账号密码
        if username == ADMIN_USER and password == ADMIN_PWD:
            # 登录成功：设置Session登录状态，保持登录
            session["is_login"] = True
            # 跳转到你的后台首页（admin_dashboard）
            return redirect(url_for("admin_dashboard"))
        else:
            # 登录失败：向前端传错误提示，重新渲染登录页
            flash("Wrong username or password! Please try again.")
            return render_template('admin/login.html')
        
    # GET请求：直接渲染登录页    
    return render_template('admin/login.html')

# 后台首页（控制台）
@app.route('/admin/dashboard')
@admin_required  # 新增：未登录禁止访问
def admin_dashboard():
    # 连接数据库，查所有文章（按ID倒序，最新的在最前面）
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    # 2. 新增：查询文章总数
    total_posts = conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    # 3. 新增：查询分类总数（去重）
    total_categories = conn.execute('SELECT COUNT(DISTINCT category) FROM posts').fetchone()[0]
    conn.close()
    # 传递posts数据到前端，用于动态渲染
    return render_template(
        'admin/dashboard.html', 
        posts=posts,
        total_posts=total_posts,  # 文章总数
        total_categories=total_categories  # 分类总数)
    )    

# 发布文章页
@app.route('/admin/create')
@admin_required  # 新增：未登录禁止访问
def admin_create_post():
    return render_template('admin/create_post.html')

# 编辑文章页
@app.route('/admin/edit/<int:post_id>', methods=['GET'])
@admin_required  # 新增：未登录禁止访问
def admin_edit_post(post_id):
    # 1. 连接数据库，按ID查询文章
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    
    # 2. 处理文章不存在的情况（防止手动输入错误ID）
    if not post:
        flash("Article not found!")
        return redirect(url_for("admin_dashboard"))
    
    # 3. 传递数据库查询的真实数据到编辑页，自动回显
    return render_template('admin/edit_post.html', post=post)

# 富文本编辑器图片上传接口
@app.route('/admin/upload_image', methods=['POST'])
@admin_required  # 新增：未登录禁止访问
def upload_image():
    # 1. 获取上传的图片文件
    file = request.files.get('file')
    if not file:
        return jsonify({'code': 1, 'msg': 'No file uploaded'})

    # 2. 生成唯一文件名（避免重名），用时间戳+原文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}_{file.filename}"
    # 图片保存路径：static/uploads
    upload_path = os.path.join(app.root_path, 'static', 'uploads', filename)

    # 3. 保存图片到本地
    file.save(upload_path)

    # 4. 返回图片 URL（前台访问路径）
    image_url = f"/static/uploads/{filename}"
    return jsonify({'code': 0, 'data': {'location': image_url}})

# 发布文章 POST 路由（后续完善数据库保存，先测试表单）
@app.route('/admin/create', methods=['POST'])
@admin_required  # 新增：未登录禁止访问
def admin_create_post_submit():
    title = request.form.get('title')
    category = request.form.get('category')
    content = request.form.get('content')  # 这里直接获取富文本 HTML 内容

    # 2. 简单表单验证（防止空内容提交）
    if not title or not category or not content:
        flash("Title, category and content cannot be empty!")
        return redirect(url_for("admin_create_post"))  # 跳回发布页，提示错误
    

    # 3. 连接数据库，插入文章数据
    conn = get_db_connection()
    try:
        # 插入SQL：包含标题、分类、富文本内容、发布时间
        conn.execute('''
            INSERT INTO posts (title, category, content, date)
            VALUES (?, ?, ?, ?)
        ''', (title, category, content, datetime.now().strftime('%Y-%m-%d %I:%M %p')))  # datetime.now()获取当前时间
        conn.commit()  # 提交事务，确保数据存入数据库
        # 获取刚插入的文章ID
        post_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    finally:
        conn.close()  # 无论成功失败，都关闭数据库连接
    
    # 4. 发布成功：跳转到后台首页
    flash("Post published successfully!")
    return redirect(url_for("admin_dashboard"))

# 编辑文章 POST 路由
@app.route('/admin/edit/<int:post_id>', methods=['POST'])
@admin_required  # 新增：未登录禁止访问
def admin_edit_post_submit(post_id):
    # 1. 获取前端修改后的表单数据
    title = request.form.get('title') 
    category = request.form.get('category')
    content = request.form.get('content')

    # 2. 表单非空验证
    if not title or not category or not content:
        flash("Title, category and content cannot be empty!")
        return redirect(url_for("admin_edit_post", post_id=post_id))  # 跳回当前编辑页
    
    # 3. 连接数据库，更新数据
    conn = get_db_connection()
    try:
        # 先查询文章是否存在
        post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
        if not post:
            flash("Article not found!")
            return redirect(url_for("admin_dashboard"))
        
        # 更新数据库：适配`date`字段（
        conn.execute('''
            UPDATE posts 
            SET title = ?, category = ?, content = ?, date = ?
            WHERE id = ?
        ''', (title, category, content, datetime.now().strftime('%Y-%m-%d %I:%M %p'), post_id))  # 更新修改时间为当前时间
        conn.commit()
    finally:
        conn.close()
    
    # 4. 编辑成功，跳后台首页并提示
    flash("Article updated successfully!")
    return redirect(url_for("admin_dashboard"))

# 新增：删除文章路由
@app.route('/admin/delete/<int:post_id>')
@admin_required
def admin_delete_post(post_id):
    # 1. 连接数据库，检查文章是否存在
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if not post:
        flash("Article not found!")
        conn.close()
        return redirect(url_for("admin_dashboard"))
    
    # 2. 删除对应ID的文章
    try:
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        flash("Article deleted successfully!")
    finally:
        conn.close()
    
    # 3. 删除成功，跳后台首页
    return redirect(url_for("admin_dashboard"))

# 退出登录
@app.route('/admin/logout')
@admin_required  # 新增：必须是登录了，才能退出
def admin_logout():
    # 清除Session中的登录状态，销毁登录
    session.pop("is_login", None)
    # 跳回后台登录页
    return redirect(url_for("admin_login"))

# Run app in debug mode
if __name__ == '__main__':
    app.run(debug=True)