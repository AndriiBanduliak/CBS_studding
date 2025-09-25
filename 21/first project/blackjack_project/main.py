# main.py
# Главный исполняемый файл игры.
# Отвечает за пользовательский интерфейс в консоли и управление игровым циклом.

from blackjack_package.game_logic import BlackjackGame
from blackjack_package.models import GameState

def play_game_in_console():
    """Запускает и управляет основным циклом игры в блэкджек в консоли."""
    game = BlackjackGame()
    print("Добро пожаловать в Blackjack!")
    
    while game.balance > 0:
        game.start_new_game()
        print(f"\n{'='*20}\nНОВЫЙ РАУНД\nВаш баланс: ${game.balance}")
        
        while True:
            try:
                bet_input = input("Введите вашу ставку (или 'q' для выхода): ")
                if bet_input.lower() == 'q':
                    print("Спасибо за игру!")
                    return
                bet = int(bet_input)
                if game.place_bet(bet): break
                else: print("Неверная ставка. Убедитесь, что она не превышает ваш баланс.")
            except ValueError:
                print("Пожалуйста, введите целое число.")
        
        print("\nВаши карты:", *[str(card) for card in game.player_hand.cards], sep=' ')
        print(f"Сумма: {game.player_hand.value}")
        print("\nКарта дилера:", str(game.dealer_hand.cards[0]), "[Скрытая карта]")
        
        while game.state == GameState.PLAYER_TURN:
            print(f"\nПодсказка: {game.get_hint()}")
            action = input("Выберите действие (1-Взять, 2-Стоять, 3-Удвоить): ").strip()
            
            if action == "1":
                game.hit()
                print("\nВаши карты:", *[str(card) for card in game.player_hand.cards], sep=' ')
                print(f"Сумма: {game.player_hand.value}")
            elif action == "2": game.stand()
            elif action == "3":
                if not game.double_down():
                    print("Удвоение сейчас невозможно.")
            else: print("Неверный ввод.")
        
        if game.state == GameState.GAME_OVER:
            print("\n--- РЕЗУЛЬТАТ РАУНДА ---")
            print("Карты дилера:", *[str(card) for card in game.dealer_hand.cards], sep=' ')
            print(f"Сумма дилера: {game.dealer_hand.value}")
            print(f"\n{game.result}")
            print(f"Итоговый баланс: ${game.balance}")
            
    print("\nУ вас закончились деньги! Игра окончена.")

if __name__ == "__main__":
    play_game_in_console()
