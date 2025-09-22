# Blackjack Web Application

A web-based version of the classic card game Blackjack where users play against an automated dealer.

## Features

- **Game Logic**: Standard Blackjack rules with options to Hit, Stand, and Double Down
- **User Authentication**: Secure registration and login system with email verification
- **Personal Account**: User profiles with game statistics and history
- **In-Game Hints**: Strategy suggestions based on basic Blackjack strategy
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Backend**: Python with Flask framework
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **Database**: SQLite (can be configured for PostgreSQL or MySQL)
- **Authentication**: Flask-Login for user management
- **Email**: Flask-Mail for verification and password reset

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env` file:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///blackjack.db
   MAIL_SERVER=your-mail-server
   MAIL_PORT=your-mail-port
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email
   MAIL_PASSWORD=your-password
   MAIL_DEFAULT_SENDER=your-email
   ```
4. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
5. Run the application:
   ```
   python app.py
   ```

## Game Rules

- **Objective**: Get a hand value closer to 21 than the dealer without exceeding 21
- **Card Values**:
  - Cards 2-10 are worth their face value
  - Face cards (J, Q, K) are worth 10
  - Aces are worth 1 or 11, whichever is more advantageous
- **Actions**:
  - **Hit**: Take another card
  - **Stand**: Take no more cards
  - **Double Down**: Double your bet and take one more card
- **Dealer Rules**: The dealer must hit until their hand totals 17 or higher
- **Winning**: You win if your hand is closer to 21 than the dealer without busting
- **Blackjack**: An Ace and a 10-value card as your first two cards pays 3:2

## Project Structure

```
blackjack/
├── app.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── blackjack/              # Main package
│   ├── __init__.py         # Application factory
│   ├── models.py           # Database models
│   ├── auth/               # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── routes.py       # Auth routes
│   │   ├── forms.py        # Auth forms
│   │   └── email.py        # Email functionality
│   ├── main/               # Main blueprint
│   │   ├── __init__.py
│   │   └── routes.py       # Main routes
│   ├── game/               # Game blueprint
│   │   ├── __init__.py
│   │   ├── routes.py       # Game routes
│   │   └── blackjack.py    # Game logic
│   ├── static/             # Static files
│   │   ├── css/
│   │   └── img/
│   └── templates/          # HTML templates
│       ├── auth/
│       ├── main/
│       ├── game/
│       └── email/
```

## Future Enhancements

- Multiplayer functionality
- Additional betting options (Insurance, Split)
- Leaderboards and achievements
- More detailed statistics and analytics
- Custom card deck themes

## License

This project is licensed under the MIT License - see the LICENSE file for details.