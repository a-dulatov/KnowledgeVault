# Knowledge Base Application

## Overview

This is a Django-based knowledge base application designed to help organizations create, manage, and share documentation and articles. The application provides a structured way to organize content through spaces, categories, and labels, with features for collaboration, sharing, and content management.

## System Architecture

### Backend Architecture
- **Framework**: Django 5.2 with Python 3.11
- **WSGI Server**: Gunicorn for production deployment
- **Database**: PostgreSQL 16 configured but not yet implemented (uses JSON files for data storage currently)
- **Authentication**: Django's built-in authentication system
- **Rich Text Editing**: TinyMCE integration for content creation

### Frontend Architecture
- **Template Engine**: Django templates with Jinja2-style syntax
- **UI Framework**: Bootstrap 5.3 for responsive design
- **Icons**: Font Awesome 6.4 for iconography
- **Code Highlighting**: Highlight.js for syntax highlighting
- **JavaScript**: Vanilla JavaScript for interactive features

### File Structure
- **Templates**: Located in `templates/` directory with a base layout and specific page templates
- **Static Files**: TinyMCE editor files stored in `staticfiles/tinymce/`
- **Configuration**: Django settings managed through `knowledgebase.settings`
- **Data Storage**: Currently using JSON files in `data/` directory (transitional approach)

## Key Components

### Content Management
- **Articles**: Primary content units with rich text content, categories, and tags
- **Paragraphs**: Structured content sections within articles with attachment support
- **Spaces**: Organizational containers for grouping related articles
- **Categories**: Classification system for articles
- **Labels**: Color-coded tags for additional organization

### User Features
- **Authentication**: User registration, login, and session management
- **Favorites**: Personal bookmarking system for articles
- **Read Later**: Personal reading queue functionality
- **Read Tracking**: Progress tracking for articles
- **Comments**: Threaded commenting system on articles

### Sharing and Collaboration
- **Secure Sharing**: Time-limited sharing links for articles and paragraphs
- **PDF Export**: Article export to PDF format using WeasyPrint
- **Social Sharing**: Integration with social media platforms
- **Public/Private Content**: Content visibility controls

### Search and Discovery
- **Full-text Search**: Article content searching capability
- **Filtering**: Multi-criteria filtering by spaces, labels, and categories
- **Navigation**: Hierarchical navigation through content organization

## Data Flow

### Current Implementation
1. **Data Storage**: Articles stored in `data/articles.json` file
2. **Template Rendering**: Django views render templates with JSON data
3. **User Interactions**: Form submissions processed through Django views
4. **Static Content**: TinyMCE and Bootstrap assets served statically

### Database Migration Path
The application is designed to migrate from JSON file storage to PostgreSQL:
1. **Models**: Django models defined for all content types
2. **Migrations**: Database schema creation through Django migrations
3. **Data Migration**: JSON data conversion to database records
4. **ORM Integration**: Replace JSON file operations with Django ORM queries

## External Dependencies

### Python Packages
- **Django**: Web framework and ORM
- **Flask**: Minimal web framework (legacy dependency)
- **TinyMCE**: Rich text editor integration
- **WeasyPrint**: PDF generation with CSS support
- **psycopg2**: PostgreSQL database adapter
- **Gunicorn**: WSGI HTTP server
- **Markdown**: Markdown parsing support
- **Bleach**: HTML sanitization
- **OpenAI & Anthropic**: AI integration capabilities

### Frontend Dependencies
- **Bootstrap 5.3**: CSS framework via CDN
- **Font Awesome 6.4**: Icon library via CDN
- **Highlight.js**: Code syntax highlighting via CDN
- **TinyMCE**: Rich text editor (self-hosted)

## Deployment Strategy

### Development Environment
- **Local Server**: Django development server on port 5000
- **Hot Reload**: Automatic reloading for development changes
- **Debug Mode**: Detailed error reporting and debugging tools

### Production Deployment
- **WSGI Server**: Gunicorn with autoscale deployment target
- **Port Configuration**: External port 80 mapped to internal port 5000
- **Process Management**: Replit workflows for application lifecycle
- **Static Files**: Served through Django's static files handling

### Infrastructure Requirements
- **Python 3.11**: Runtime environment
- **PostgreSQL 16**: Database server
- **System Libraries**: Font rendering, PDF generation, and SSL support
- **File Storage**: Local filesystem for uploads and attachments

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- June 17, 2025. Initial setup