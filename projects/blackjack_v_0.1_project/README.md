# 🃏 Blackjack Web Application

A professional, feature-rich web application for playing Blackjack (21) built with Flask. This application provides a complete casino-style experience with user authentication, game statistics, and real-time gameplay.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0.1-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### Core Game Features
- **Complete Blackjack Logic**: Implements standard casino rules with proper card handling
- **Multiple Actions**: Hit, Stand, Double Down
- **Strategic Hints**: Real-time suggestions based on basic Blackjack strategy charts
- **Dealer AI**: Automatic dealer play following standard rules (hits on soft 17)
- **Virtual Currency**: Starting balance system with win/loss tracking

### User Features
- **Secure Authentication**: User registration and login with email verification
- **Password Reset**: Secure password recovery via email tokens
- **User Profiles**: Customizable avatars and detailed statistics
- **Game History**: Complete log of all games played with results
- **Statistics Dashboard**: Win/loss ratios, biggest wins, and game counts

### Technical Features
- **RESTful API**: Clean JSON API for game interactions
- **Session Management**: Secure game state persistence
- **Database Migrations**: Flask-Migrate for schema versioning
- **Logging System**: Comprehensive logging with file rotation
- **Error Handling**: Robust error handling and validation
- **Responsive Design**: Mobile-friendly UI with modern styling

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- A mail server or SMTP credentials (for email verification)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/blackjack.git
   cd blackjack
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///blackjack.db
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

   > **Note**: For Gmail, you'll need to generate an [App Password](https://support.google.com/accounts/answer/185833) if you have 2FA enabled.

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   
   Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
blackjack/
├── app.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in repo)
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
│
├── blackjack/                  # Main application package
│   ├── __init__.py            # Application factory
│   ├── models.py              # SQLAlchemy database models
│   ├── logger.py              # Logging configuration
│   │
│   ├── auth/                  # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── routes.py          # Auth routes (login, register, etc.)
│   │   ├── forms.py           # WTForms for authentication
│   │   └── email.py           # Email sending utilities
│   │
│   ├── main/                  # Main application blueprint
│   │   ├── __init__.py
│   │   ├── routes.py          # Main routes (profile, home)
│   │   └── forms.py           # Profile forms
│   │
│   ├── game/                  # Game blueprint
│   │   ├── __init__.py
│   │   ├── routes.py          # Game API endpoints
│   │   └── blackjack.py       # Core game logic
│   │
│   ├── static/                # Static files
│   │   ├── css/              # Stylesheets
│   │   ├── js/               # JavaScript files
│   │   └── img/              # Images and avatars
│   │
│   ├── templates/             # Jinja2 templates
│   │   ├── auth/             # Auth templates
│   │   ├── main/             # Main templates
│   │   ├── game/             # Game templates
│   │   └── email/            # Email templates
│   │
│   └── logs/                  # Application logs (generated)
│
└── tests/                     # Test suite
    └── test_blackjack.py      # Game logic tests
```

## 🎮 Game Rules

This implementation follows standard casino Blackjack rules:

### Objective
Get a hand value closer to 21 than the dealer without exceeding 21.

### Card Values
- **Number cards (2-10)**: Face value
- **Face cards (J, Q, K)**: 10 points
- **Aces**: 1 or 11 (whichever is more advantageous)

### Player Actions
- **Hit**: Take another card
- **Stand**: Take no more cards, dealer plays
- **Double Down**: Double your bet, take exactly one more card

### Dealer Rules
- Dealer must hit on 16 or lower
- Dealer must stand on 17 or higher
- Dealer's first card is hidden until player stands

### Winning Conditions
- **Blackjack**: Ace + 10-value card = 3:2 payout
- **Win**: Hand closer to 21 than dealer
- **Push**: Same value as dealer (bet returned)
- **Bust**: Hand exceeds 21 (automatic loss)

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Or using unittest:

```bash
python -m unittest discover tests
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | `dev` (⚠️ change in production) |
| `DATABASE_URL` | Database connection string | `sqlite:///blackjack.db` |
| `MAIL_SERVER` | SMTP server hostname | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP server port | `587` |
| `MAIL_USE_TLS` | Use TLS encryption | `True` |
| `MAIL_USERNAME` | SMTP username | - |
| `MAIL_PASSWORD` | SMTP password | - |
| `MAIL_DEFAULT_SENDER` | Default sender email | - |

### Database

The application uses SQLite by default but can be configured to use PostgreSQL or MySQL by changing the `DATABASE_URL`:

```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/blackjack

# MySQL
DATABASE_URL=mysql://user:password@localhost/blackjack
```

## 🛠️ Development

### Running in Development Mode

```bash
python app.py
```

The app runs with debug mode enabled by default in development.

### Database Migrations

When modifying models, create a new migration:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### Code Style

This project follows PEP 8 style guidelines. Consider using:
- `black` for code formatting
- `flake8` for linting
- `pylint` for additional checks

## 📝 API Endpoints

### Game Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/game/` | Game interface | ✅ |
| POST | `/game/start` | Start new game | ✅ |
| POST | `/game/bet` | Place bet | ✅ |
| POST | `/game/hit` | Take a card | ✅ |
| POST | `/game/stand` | End turn | ✅ |
| POST | `/game/double` | Double down | ✅ |
| GET | `/game/hint` | Get strategy hint | ✅ |

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | User login |
| GET | `/logout` | User logout |
| GET | `/verify/<token>` | Email verification |
| GET/POST | `/reset_password_request` | Request password reset |
| GET/POST | `/reset_password/<token>` | Reset password |

## 🚢 Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `FLASK_ENV=production`
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up proper SMTP server
- [ ] Enable HTTPS
- [ ] Configure proper logging
- [ ] Set up database backups
- [ ] Use a production WSGI server (gunicorn, uWSGI)
- [ ] Configure reverse proxy (nginx)

### Example with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

Your Name - [@AndriiBanduliak](https://github.com/AndriiBanduliak)
## 🙏 Acknowledgments

- Flask community for the excellent framework
- Blackjack strategy charts for hint implementation
- All contributors and testers

## 🔮 Future Enhancements

- [ ] Split pairs functionality
- [ ] Insurance bets
- [ ] Multi-deck support
- [ ] Leaderboards
- [ ] Tournament mode
- [ ] Real-time multiplayer
- [ ] Customizable table themes
- [ ] Advanced statistics and analytics
- [ ] API documentation with Swagger/OpenAPI

---

**Made with ♠️♥️♦️♣️ and Python**
