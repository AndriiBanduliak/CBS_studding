from blackjack.game.blackjack import Card, Deck, Hand, BlackjackGame, Suit, GameState

def test_game():
    # Создаем игру
    game = BlackjackGame()
    print("Игра создана")
    
    # Начинаем новую игру
    game.start_new_game()
    print(f"Новая игра начата, состояние: {game.state}")
    
    # Делаем ставку
    game.place_bet(50)
    print(f"Ставка сделана: {game.bet}")
    print(f"Состояние игры: {game.state}")
    
    # Показываем карты игрока
    print("\nКарты игрока:")
    for card in game.player_hand.cards:
        print(f"  {card}")
    print(f"Значение руки игрока: {game.player_hand.value}")
    
    # Показываем карты дилера
    print("\nКарты дилера:")
    for card in game.dealer_hand.cards:
        print(f"  {card}")
    print(f"Значение руки дилера: {game.dealer_hand.value}")
    
    # Получаем подсказку
    hint = game.get_hint()
    print(f"\nПодсказка: {hint}")
    
    # Игрок берет карту
    game.hit()
    print("\nИгрок взял карту")
    print("Карты игрока:")
    for card in game.player_hand.cards:
        print(f"  {card}")
    print(f"Значение руки игрока: {game.player_hand.value}")
    
    # Игрок останавливается
    game.stand()
    print("\nИгрок остановился")
    print(f"Состояние игры: {game.state}")
    
    # Показываем результат
    print(f"\nРезультат игры: {game.result}")
    print(f"Выигрыш: {game.payout}")

if __name__ == "__main__":
    test_game()