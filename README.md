# My Tech Blog
A personal technical blog project developed with Python, Flask, and SQLite, focusing on sharing technical notes, research reports, and development experiences.

## Project Overview
This project aims to build a lightweight, accessible personal tech blog, supporting article display, category filtering, keyword search, and admin management (CRUD operations for articles). It adopts a simple front-end and back-end separation architecture, suitable for beginners to practice Web development.

## Core Features
- **Admin Panel**: Secure login, article CRUD, image upload for rich text
- **Front-end**: Article display, category filter, search, responsive design
- **Rich Text Editor**: TinyMCE integration with local image upload
- **Database**: SQLite (no complex configuration, out of the box)
- **UI/UX**: Flash messages (success/error), nav highlight, image adaption

### Frontend
- Clean post list display (sorted by latest first)
- Post detail page with formatted content and images
- Category filter and post search (frontend)
- Responsive design for all devices

## Tech Stack
- **Backend**: Flask, Flask-Login, SQLite3
- **Frontend**: HTML5, CSS3, JavaScript, TinyMCE (Rich Text Editor)
- **Deployment**: PythonAnywhere (free) / Any Linux server
- **Security**: Password hashing, CSRF protection, unauthorized access control

## Quick Start (Local Run)
### Prerequisites
- Python 3.8+
- Pip (Python package manager)

### Run the App Locally
1. Clone the repository 
   ```bash
   git clone https://github.com/nqilin/my_tech_blog.git
   cd my_tech_blog
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Flask app
   ```bash
   python app.py
   ```
4. Access the app
   - Frontend: http://127.0.0.1:5000
   - Admin Panel: http://127.0.0.1:5000/admin/login (use your admin account)

## Deployment (Free on PythonAnywhere)
This blog can be deployed for free on **PythonAnywhere** (Python-specific hosting). Check the deployment steps below:
1. Register a free PythonAnywhere account: https://www.pythonanywhere.com/
2. Pull the code from this GitHub repository
3. Configure WSGI and reload the app
4. Access via your unique domain: `[你的PythonAnywhere用户名].pythonanywhere.com`

## Project Structure
```
your-blog/
├── app.py               # Main Flask app (routes, database, logic)
├── app.db               # SQLite3 database (auto-generated)
├── static/              # Static files (CSS, JS, uploaded images)
│   ├── css/             # Style sheets
│   ├── js/              # JavaScript files
│   └── uploads/         # Uploaded blog images
├── templates/           # HTML templates
│   ├── admin/           # Admin panel templates
│   └── front/           # Frontend templates
├── README.md            # Project documentation
├── .gitignore           # Ignored files for Git
└── requirements.txt     # Project dependencies
```

## License
MIT License - feel free to use, modify and distribute this project.

## Author
**Vatey** - [vateyhul](https://github.com/nqilin/vateyHul)