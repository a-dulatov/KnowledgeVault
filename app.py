import os
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Load data from JSON files
def load_articles():
    try:
        with open('data/articles.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Initialize with default articles if file doesn't exist
        default_articles = [
            {
                "id": 1,
                "title": "Getting Started with Flask",
                "content": "<p>Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications. It began as a simple wrapper around Werkzeug and Jinja and has become one of the most popular Python web application frameworks.</p><h3>Installation</h3><p>You can install Flask using pip:</p><pre><code>pip install Flask</code></pre><h3>Hello World Example</h3><p>Here's a simple Flask application:</p><pre><code>from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef hello_world():\n    return 'Hello, World!'\n\nif __name__ == '__main__':\n    app.run(debug=True)</code></pre>",
                "summary": "Learn the basics of Flask, a lightweight Python web framework.",
                "category_id": 1,
                "tags": ["flask", "python", "web development"],
                "created_at": "2023-01-15",
                "updated_at": "2023-01-15"
            },
            {
                "id": 2,
                "title": "Understanding RESTful APIs",
                "content": "<p>REST (Representational State Transfer) is an architectural style for designing networked applications. RESTful APIs use HTTP requests to perform CRUD operations (Create, Read, Update, Delete).</p><h3>Key Principles</h3><ul><li>Stateless client-server communication</li><li>Cacheable responses</li><li>Uniform interface</li><li>Layered system</li></ul><h3>HTTP Methods</h3><p>RESTful APIs use standard HTTP methods:</p><ul><li>GET: Retrieve a resource</li><li>POST: Create a new resource</li><li>PUT: Update an existing resource</li><li>DELETE: Remove a resource</li></ul>",
                "summary": "A guide to RESTful API principles and implementation.",
                "category_id": 2,
                "tags": ["api", "rest", "http", "web development"],
                "created_at": "2023-02-10",
                "updated_at": "2023-02-12"
            },
            {
                "id": 3,
                "title": "JavaScript Fundamentals",
                "content": "<p>JavaScript is a high-level, interpreted programming language that conforms to the ECMAScript specification. It's a core technology of the web, enabling interactive web pages and client-side applications.</p><h3>Variables</h3><p>JavaScript has three ways to declare variables:</p><pre><code>var x = 5;      // function scoped\nlet y = 6;      // block scoped\nconst z = 7;    // block scoped constant</code></pre><h3>Functions</h3><p>Functions are first-class objects in JavaScript:</p><pre><code>function greet(name) {\n    return `Hello, ${name}!`;\n}\n\nconst sayHello = (name) => `Hello, ${name}!`;</code></pre>",
                "summary": "Core concepts of JavaScript programming language.",
                "category_id": 3,
                "tags": ["javascript", "programming", "web development"],
                "created_at": "2023-03-05",
                "updated_at": "2023-03-06"
            },
            {
                "id": 4,
                "title": "Introduction to Bootstrap",
                "content": "<p>Bootstrap is a free and open-source CSS framework directed at responsive, mobile-first front-end web development. It contains HTML, CSS, and JavaScript-based design templates for typography, forms, buttons, navigation, and other interface components.</p><h3>Getting Started</h3><p>Include Bootstrap in your project:</p><pre><code>&lt;link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css\" rel=\"stylesheet\"&gt;\n&lt;script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js\"&gt;&lt;/script&gt;</code></pre><h3>Grid System</h3><p>Bootstrap's grid system uses containers, rows, and columns to layout content:</p><pre><code>&lt;div class=\"container\"&gt;\n  &lt;div class=\"row\"&gt;\n    &lt;div class=\"col-md-6\"&gt;Column 1&lt;/div&gt;\n    &lt;div class=\"col-md-6\"&gt;Column 2&lt;/div&gt;\n  &lt;/div&gt;\n&lt;/div&gt;</code></pre>",
                "summary": "Learn how to use Bootstrap for responsive web design.",
                "category_id": 4,
                "tags": ["bootstrap", "css", "responsive design", "web development"],
                "created_at": "2023-04-20",
                "updated_at": "2023-04-22"
            },
            {
                "id": 5,
                "title": "Database Design Principles",
                "content": "<p>Effective database design is crucial for creating applications that are performant, scalable, and maintainable. This article covers key principles to follow when designing databases.</p><h3>Normalization</h3><p>Normalization is the process of organizing data to reduce redundancy and improve data integrity:</p><ul><li>First Normal Form (1NF): Eliminate duplicate columns</li><li>Second Normal Form (2NF): Meet 1NF and remove partial dependencies</li><li>Third Normal Form (3NF): Meet 2NF and remove transitive dependencies</li></ul><h3>Indexing</h3><p>Proper indexing improves query performance:</p><ul><li>Create indexes on frequently queried columns</li><li>Avoid over-indexing as it slows down write operations</li><li>Consider composite indexes for queries with multiple conditions</li></ul>",
                "summary": "Essential principles for designing efficient databases.",
                "category_id": 5,
                "tags": ["database", "sql", "normalization", "indexing"],
                "created_at": "2023-05-15",
                "updated_at": "2023-05-16"
            }
        ]
        # Create directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        # Save default articles
        with open('data/articles.json', 'w') as file:
            json.dump(default_articles, file, indent=4)
        return default_articles

def load_categories():
    try:
        with open('data/categories.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Initialize with default categories if file doesn't exist
        default_categories = [
            {
                "id": 1,
                "name": "Flask",
                "description": "Articles about Flask web framework"
            },
            {
                "id": 2,
                "name": "API Development",
                "description": "Articles about API design and implementation"
            },
            {
                "id": 3,
                "name": "JavaScript",
                "description": "Articles about JavaScript programming"
            },
            {
                "id": 4,
                "name": "Frontend Frameworks",
                "description": "Articles about CSS and frontend frameworks"
            },
            {
                "id": 5,
                "name": "Databases",
                "description": "Articles about database design and usage"
            }
        ]
        # Create directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        # Save default categories
        with open('data/categories.json', 'w') as file:
            json.dump(default_categories, file, indent=4)
        return default_categories

# Routes
@app.route('/')
def index():
    articles = load_articles()
    categories = load_categories()
    # Get the 3 most recent articles for the homepage
    recent_articles = sorted(articles, key=lambda x: x['created_at'], reverse=True)[:3]
    return render_template('index.html', recent_articles=recent_articles, categories=categories)

@app.route('/article/<int:article_id>')
def article(article_id):
    articles = load_articles()
    categories = load_categories()
    article = next((a for a in articles if a['id'] == article_id), None)
    
    if not article:
        return render_template('index.html', error="Article not found", categories=categories)
    
    # Find the category for this article
    category = next((c for c in categories if c['id'] == article['category_id']), None)
    
    # Find related articles (same category, excluding current article)
    related_articles = [a for a in articles if a['category_id'] == article['category_id'] and a['id'] != article_id][:3]
    
    return render_template('article.html', article=article, category=category, 
                          related_articles=related_articles, categories=categories)

@app.route('/category/<int:category_id>')
def category(category_id):
    articles = load_articles()
    categories = load_categories()
    category = next((c for c in categories if c['id'] == category_id), None)
    
    if not category:
        return render_template('index.html', error="Category not found", categories=categories)
    
    # Filter articles by category
    category_articles = [a for a in articles if a['category_id'] == category_id]
    
    return render_template('category.html', category=category, 
                          articles=category_articles, categories=categories)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    articles = load_articles()
    categories = load_categories()
    
    if not query:
        return render_template('search.html', articles=[], query="", categories=categories)
    
    # Filter articles based on search query
    results = []
    for article in articles:
        if (query.lower() in article['title'].lower() or 
            query.lower() in article['content'].lower() or
            query.lower() in article['summary'].lower() or
            any(query.lower() in tag.lower() for tag in article['tags'])):
            results.append(article)
    
    return render_template('search.html', articles=results, query=query, categories=categories)

# API Endpoints
@app.route('/api/articles')
def get_articles():
    articles = load_articles()
    return jsonify(articles)

@app.route('/api/articles/<int:article_id>')
def get_article(article_id):
    articles = load_articles()
    article = next((a for a in articles if a['id'] == article_id), None)
    if article:
        return jsonify(article)
    return jsonify({"error": "Article not found"}), 404

@app.route('/api/categories')
def get_categories():
    categories = load_categories()
    return jsonify(categories)

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    articles = load_articles()
    
    if not query:
        return jsonify([])
    
    # Filter articles based on search query
    results = []
    for article in articles:
        if (query.lower() in article['title'].lower() or 
            query.lower() in article['content'].lower() or
            query.lower() in article['summary'].lower() or
            any(query.lower() in tag.lower() for tag in article['tags'])):
            results.append(article)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
