# 🌌 CosmicFinance

<div align="center">

**A modern, beautiful, and feature-rich personal finance tracking application**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API Documentation](#-api-documentation) • [Screenshots](#-screenshots)

</div>

---

## 📖 Overview

**CosmicFinance** is a full-stack web application for tracking personal income and expenses with a stunning cosmic-themed UI. Built with Django REST Framework and featuring a modern, responsive frontend, it provides comprehensive financial management tools with beautiful visualizations and intuitive user experience.

### Key Highlights

- 🎨 **Stunning Cosmic Design** - Beautiful dark/light theme with animated backgrounds and glassmorphism effects
- 📊 **Interactive Charts** - Real-time data visualization with Chart.js
- 🔐 **Secure Authentication** - JWT-based authentication system
- 📱 **Fully Responsive** - Optimized for desktop, tablet, and mobile devices
- ⚡ **Fast & Efficient** - Optimized database queries with Django ORM aggregations
- 🎯 **Feature-Rich** - Budget tracking, data export, sorting, filtering, and more

---

## ✨ Features

### Core Functionality
- **User Management**
  - User registration and authentication
  - JWT token-based secure login
  - User profile management

- **Category Management**
  - Create custom income and expense categories
  - Organize transactions by category
  - Visual category indicators

- **Transaction Tracking**
  - Add, edit, and delete transactions
  - Automatic categorization
  - Date-based filtering and sorting
  - Search functionality

- **Analytics & Reports**
  - Monthly income/expense summaries
  - Category-wise spending analysis
  - Interactive bar and doughnut charts
  - Real-time statistics dashboard

### Advanced Features
- **Budget Management**
  - Set monthly budget limits
  - Visual budget progress tracking
  - Color-coded budget alerts (green/yellow/red)

- **Data Export**
  - Export transactions to CSV format
  - Complete data backup functionality

- **User Experience**
  - Dark/Light theme with automatic system preference detection
  - Smooth animations and transitions
  - Toast notifications for user feedback
  - Keyboard shortcuts (Ctrl+K for theme, Ctrl+E for export, Ctrl+N for quick add)
  - Quick action floating buttons
  - Counter animations for statistics

- **Mobile Optimization**
  - Fully responsive design
  - Touch-friendly interface
  - Optimized layouts for small screens

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Authentication**: djangorestframework-simplejwt 5.3.0
- **Database**: PostgreSQL 12+
- **Filtering**: django-filter 23.3
- **Testing**: pytest 7.4.3, pytest-django 4.7.0

### Frontend
- **Styling**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **Charts**: Chart.js 4.4.0
- **Fonts**: Google Fonts (Inter, Space Grotesk)
- **JavaScript**: Vanilla ES6+

### Architecture
- **Service Layer Pattern** - Business logic separated from views
- **RESTful API** - Clean API design following REST principles
- **ORM Optimizations** - Efficient database queries with aggregations
- **Responsive Design** - Mobile-first approach

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)
- virtualenv (recommended)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd cosmic-finance
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up PostgreSQL

1. **Install PostgreSQL** (if not already installed)
   - Windows: Download from [PostgreSQL official website](https://www.postgresql.org/download/windows/)
   - Linux: `sudo apt install postgresql postgresql-contrib`
   - Mac: `brew install postgresql`

2. **Create Database and User**

   Connect to PostgreSQL:
   ```bash
   psql -U postgres
   ```

   Create database and user:
   ```sql
   CREATE DATABASE cosmic_finance;
   CREATE USER cosmic_user WITH PASSWORD 'your_secure_password';
   ALTER ROLE cosmic_user SET client_encoding TO 'utf8';
   ALTER ROLE cosmic_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE cosmic_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE cosmic_finance TO cosmic_user;
   \q
   ```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here-generate-new-one
DEBUG=True

# PostgreSQL Database Configuration
DB_NAME=cosmic_finance
DB_USER=cosmic_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 6: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 8: Run Development Server

```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

---

## 📖 Usage

### Getting Started

1. **Register a New Account**
   - Click on the "Register" tab in the login form
   - Fill in your username, email, and password
   - Optionally add your first and last name

2. **Login**
   - Enter your credentials
   - You'll be automatically logged in and redirected to the dashboard

3. **Create Categories**
   - Navigate to "Add Category" section
   - Enter category name and select type (Income or Expense)
   - Click "Add Category"

4. **Add Transactions**
   - Select a category from the dropdown
   - Enter amount, description (optional), and date
   - Click "Add Transaction"

5. **View Analytics**
   - Check the monthly summary chart for income/expense trends
   - View category breakdown in the doughnut chart
   - Monitor your statistics in the dashboard cards

### Keyboard Shortcuts

- `Ctrl/Cmd + K` - Toggle theme (dark/light)
- `Ctrl/Cmd + E` - Export data to CSV
- `Ctrl/Cmd + N` - Quick add transaction (scroll to form)

### Features Guide

- **Theme Switching**: Click the sun/moon icon in the navbar to toggle between dark and light themes
- **Budget Tracking**: Set a monthly budget and track your spending progress
- **Data Export**: Export all your transactions to CSV for backup or analysis
- **Search & Filter**: Use the search bar and category filter to find specific transactions
- **Sorting**: Click sort buttons to organize transactions by date or amount

---

## 🔌 API Documentation

### Authentication

All API endpoints require JWT authentication except for registration and token endpoints.

#### Get Access Token

**Endpoint:** `POST /api/auth/token/`

**Request:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Use Token

Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Endpoints

#### User Registration

**POST** `/api/auth/register/`

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Categories

**GET** `/api/categories/` - List all categories

**POST** `/api/categories/` - Create new category
```json
{
  "name": "Salary",
  "type": "Income"
}
```

#### Transactions

**GET** `/api/transactions/` - List transactions (supports filtering)

**Query Parameters:**
- `category_id` - Filter by category ID
- `date_from` - Start date (ISO 8601)
- `date_to` - End date (ISO 8601)

**POST** `/api/transactions/` - Create transaction
```json
{
  "category": 1,
  "amount": "5000.00",
  "description": "Monthly salary",
  "date": "2024-10-15T12:00:00Z"
}
```

**GET** `/api/transactions/{id}/` - Get transaction details

**PUT/PATCH** `/api/transactions/{id}/` - Update transaction

**DELETE** `/api/transactions/{id}/` - Delete transaction

#### Analytics

**GET** `/api/stats/monthly_summary/` - Monthly summary

**Query Parameters:**
- `months` - Number of months (default: 12)

**GET** `/api/stats/category_summary/` - Category summary

**Query Parameters:**
- `date_from` - Start date
- `date_to` - End date

#### Data Management

**DELETE** `/api/delete-all/` - Delete all user data (categories and transactions)

---

## 📸 Screenshots

### Dashboard View
The main dashboard provides an overview of your financial status with interactive charts and statistics.

### Dark Theme
Experience the stunning cosmic design with animated starry background and neon effects.

### Light Theme
Clean and professional light theme with excellent readability and modern aesthetics.

### Mobile View
Fully responsive design optimized for mobile devices with touch-friendly interface.

---

## 🏗️ Project Structure

```
cosmic-finance/
├── config/                 # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── users/                  # User management app
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── transactions/          # Transactions app
│   ├── models.py          # Category and Transaction models
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API views
│   ├── services.py       # Business logic (Service Layer)
│   ├── filters.py       # Query filters
│   └── urls.py
├── frontend/              # Frontend app
│   ├── templates/
│   │   └── frontend/
│   │       └── index.html  # Main frontend template
│   ├── views.py
│   └── urls.py
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🧪 Testing

Run tests using pytest:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=transactions --cov=users --cov-report=html
```

---

## 🐳 Docker Deployment

### Using Docker Compose

1. Update environment variables in `docker-compose.yml`
2. Run:
   ```bash
   docker-compose up -d
   ```
3. Access the application at `http://localhost:8000`

### Manual Docker Build

```bash
docker build -t cosmic-finance .
docker run -p 8000:8000 cosmic-finance
```

---

## 🔒 Security

- JWT token-based authentication
- User data isolation (users can only access their own data)
- Input validation at serializer level
- SQL injection protection via Django ORM
- Environment variables for sensitive data
- CSRF protection enabled

---

## 🎯 Architecture Decisions

### Service Layer Pattern
Business logic is separated from views into a dedicated service layer (`transactions/services.py`), providing:
- Clear separation of concerns
- Code reusability
- Easier testing

### ORM Optimizations
Analytical queries use Django ORM `annotate()` and `aggregate()` functions for efficient database operations without loading all data into Python memory.

### RESTful API Design
Clean API endpoints following REST principles with proper HTTP methods and status codes.

---

## 🚧 Future Enhancements

- [ ] Multi-currency support
- [ ] Recurring transactions
- [ ] Budget alerts and notifications
- [ ] Shared budgets (multi-user)
- [ ] Advanced reporting and PDF export
- [ ] Mobile app (React Native)
- [ ] Data import from CSV/Excel
- [ ] Investment tracking
- [ ] Goal setting and tracking

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact & Support

For questions, suggestions, or issues, please open an issue in the repository.

---

<div align="center">

**Made with ❤️ and 🌌 cosmic energy**

⭐ Star this repo if you find it helpful!

</div>
