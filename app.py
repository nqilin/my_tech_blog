# Import core Flask class
from flask import Flask
# 新增：导入Flask默认的模板渲染函数（核心，用于加载HTML页面）
from flask import render_template

# Initialize Flask app
app = Flask(__name__)
# 保留Day2的secret_key（后续session要用，先写上）
app.secret_key = 'Vatey_tech_blog_2026'

# 核心：模拟文章数据（list + dict，后续直接替换为数据库查询结果）
# 字段：id(唯一标识)、title(标题)、category(分类)、content(内容)、date(发布日期)
POSTS = [
    {
        'id': 1,
        'title': 'Getting Started with Flask Web Development',
        'category': 'Python',
        'content': 'Flask is a lightweight Python web framework that is perfect for beginners. This article records the basic steps of building a Flask project, including environment setup, route creation, and template rendering. We also learned how to use Jinja2 to pass data from backend to frontend and how to beautify pages with CSS.',
        'date': '2026-02-04'
    },
    {
        'id': 2,
        'title': 'How to Use Git and GitHub for Version Control',
        'category': 'Tools',
        'content': 'Git is an essential version control tool for developers. This article introduces the basic commands of Git, such as init, add, commit, pull and push. We also learned how to solve the push conflict problem and keep the commit history clean with rebase. GitHub is a great platform for hosting code and collaborating with others.',
        'date': '2026-02-05'
    },
    {
        'id': 3,
        'title': 'HTML & CSS for Beginner Web Developers',
        'category': 'Frontend',
        'content': 'HTML is the skeleton of web pages, and CSS is the skin. We learned how to build the basic structure of a web page with HTML, including header, nav, main and footer. We also used CSS to beautify the page, such as setting background color, box shadow, and hover effects. Flask uses url_for to import static resources like CSS correctly.',
        'date': '2026-02-06'
    }
]

# 改造：博客首页路由（统一视图函数名，符合英文规范）
@app.route('/')
def index():
    # 后端定义要传给前端的数据
    blog_data = {
        'title': 'Vatey Tech Blog',
        'subtitle': 'Share Technical Notes & Development Experiences',
        'latest_article_tip': 'Latest Technical Articles - Coming Soon!'
    }
    # 新增：把模拟文章数据POSTS传给前端，键名是posts
    return render_template('index.html', data=blog_data, posts=POSTS)

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

# 核心新路由：文章详情页（动态URL参数 <article_id>，接收文章ID）
@app.route('/article/<article_id>')
def article_detail(article_id):
    # 把URL参数转成整数（因为模拟数据的id是数字）
    post_id = int(article_id)
    # 根据ID从模拟数据中筛选对应的文章
    current_post = None
    for post in POSTS:
        if post['id'] == post_id:
            current_post = post
            break
    # 渲染详情页模板，传递当前文章数据
    return render_template('article.html', post=current_post)

# Run app in debug mode
if __name__ == '__main__':
    app.run(debug=True)