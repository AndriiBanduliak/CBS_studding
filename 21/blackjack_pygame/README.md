# BlackJack 21 Game with Pygame

A classic implementation of the card game BlackJack (21) featuring a full graphical user interface, built using Python and the Pygame library. This project was developed with a strong emphasis on clean architecture and Object-Oriented Programming (OOP) principles.


## 🎮 Core Features

*   **Classic BlackJack Rules:** The goal is to get a hand value of 21 or to be closer to 21 than the dealer without exceeding it.
*   **Interactive GUI:** User-friendly buttons for controlling the game flow (`Hit`, `Stand`, `New Game`).
*   **Automated Dealer:** The dealer follows standard casino rules (hits on 16 or less, stands on 17 or more).
*   **Accurate Score Calculation:** Automatic handling of Ace values (1 or 11 points).
*   **Game History:** Keeps track of the player's wins and losses across sessions.
*   **State Management:** A clear and robust game loop that manages different states: start, player's turn, dealer's turn, and end of the round.

## 🛠️ Technologies Used

*   **Language:** Python 3.x
*   **GUI Library:** Pygame

## 🏛️ Architecture and OOP

The project is structured with a clear separation of concerns, dividing the game logic from the user interface. This approach makes the codebase clean, scalable, and easy to maintain or test.

**Project Structure:**
```bash 
blackjack_pygame/
├── game_logic/ # Core game logic, independent of the UI
│ ├── card.py
│ ├── deck.py
│ └── player.py
├── ui/ # UI components and game assets
│ ├── assets/
│ │ ├── cards/
│ │ └── other/
│ └── components.py
├── main.py # Main entry point, connects logic and UI
└── requirements.txt # Python dependencies
```

**Key OOP Principles Implemented:**

*   **Encapsulation:** Each class has a single responsibility (e.g., `Deck` manages the card deck, `Player` manages the player's hand).
*   **Abstraction:** An abstract base class `AbstractPlayer` defines a common interface for both the `Player` and `Dealer`.
*   **Inheritance:** The `Player` and `Dealer` classes inherit shared functionality from `AbstractPlayer` while implementing their own unique behaviors.
*   **Composition:** The main `Game` class is composed of `Player`, `Dealer`, and `Deck` objects. The `Button` class is composed of a `Text` object.

## 🚀 Installation and Setup

Follow these steps to run the project on your local machine.

**1. Clone the Repository:**
```bash 
git clone https://github.com/AndriiBanduliak/blackjack-pygame.git
```

**2. Navigate to the Project Directory:** 
```bash 
cd blackjack-pygame 
```



**2. Create and Activate a Virtual Environment (Recommended):**
*   **Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
*   **macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

**3. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run the Application:**
```bash
python main.py
```