# Import core Flask class
from flask import Flask
# 新增：导入Flask默认的模板渲染函数（核心，用于加载HTML页面）
from flask import render_template

# Initialize Flask app
app = Flask(__name__)
# 保留Day2的secret_key（后续session要用，先写上）
app.secret_key = 'nqilin_tech_blog_2026'

# 改造：博客首页路由（统一视图函数名，符合英文规范）
@app.route('/')
def index():
    # 后端定义要传给前端的数据
    blog_data = {
        'title': 'My Tech Blog',
        'subtitle': 'Share Technical Notes & Development Experiences',
        'latest_article_tip': 'Latest Technical Articles - Coming Soon!'
    }
    # 渲染templates下的index.html，并把blog_data传给前端
    return render_template('index.html', data=blog_data)

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

# Run app in debug mode
if __name__ == '__main__':
    app.run(debug=True)