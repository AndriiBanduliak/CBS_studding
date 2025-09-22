from flask import render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from blackjack import db
from blackjack.game import game_bp
from blackjack.game.blackjack import BlackjackGame
from blackjack.models import User, GameHistory
import json

@game_bp.route('/')
@login_required
def index():
    return render_template('game/index.html', title='Blackjack Game')

@game_bp.route('/start', methods=['POST'])
@login_required
def start_game():
    # Initialize a new game
    game = BlackjackGame()
    
    # Store game state in session
    session['game'] = game_to_dict(game)
    
    return jsonify(success=True, game=session['game'])

@game_bp.route('/bet', methods=['POST'])
@login_required
def place_bet():
    bet_amount = int(request.form.get('bet_amount', 0))
    
    # Validate bet amount
    if bet_amount <= 0:
        return jsonify(success=False, error="Invalid bet amount")
    
    if bet_amount > current_user.currency_balance:
        return jsonify(success=False, error="Insufficient funds")
    
    # Load game from session
    game = dict_to_game(session.get('game', {}))
    
    # Place bet and deal initial cards
    success = game.place_bet(bet_amount)
    
    if success:
        # Update session
        session['game'] = game_to_dict(game)
        
        # Check for immediate game over (blackjack)
        if game.state.value == 'game_over':
            return save_game_result(game)
        
        return jsonify(success=True, game=session['game'])
    else:
        return jsonify(success=False, error="Invalid game state for betting")

@game_bp.route('/hit', methods=['POST'])
@login_required
def hit():
    # Load game from session
    game = dict_to_game(session.get('game', {}))
    
    # Execute hit action
    success = game.hit()
    
    # Update session
    session['game'] = game_to_dict(game)
    
    # Check for game over
    if game.state.value == 'game_over':
        return save_game_result(game)
    
    return jsonify(success=success, game=session['game'])

@game_bp.route('/stand', methods=['POST'])
@login_required
def stand():
    # Load game from session
    game = dict_to_game(session.get('game', {}))
    
    # Execute stand action
    success = game.stand()
    
    # Update session
    session['game'] = game_to_dict(game)
    
    # Game is always over after stand
    return save_game_result(game)

@game_bp.route('/double', methods=['POST'])
@login_required
def double_down():
    # Load game from session
    game = dict_to_game(session.get('game', {}))
    
    # Check if player has enough balance
    if game.bet > current_user.currency_balance:
        return jsonify(success=False, error="Insufficient funds for doubling down")
    
    # Execute double down action
    success = game.double_down()
    
    # Update session
    session['game'] = game_to_dict(game)
    
    # Game is always over after double down
    return save_game_result(game)

@game_bp.route('/hint', methods=['GET'])
@login_required
def get_hint():
    # Load game from session
    game = dict_to_game(session.get('game', {}))
    
    # Get hint
    hint = game.get_hint()
    
    return jsonify(success=True, hint=hint)

def save_game_result(game):
    """Save game result to database and update user statistics"""
    if game.state.value != 'game_over':
        return jsonify(success=False, error="Game is not over yet")
    
    # Update user balance
    current_user.currency_balance += game.payout
    
    # Update user statistics
    current_user.games_played += 1
    
    if game.payout > 0:
        current_user.games_won += 1
        if game.payout > current_user.biggest_win:
            current_user.biggest_win = game.payout
    elif game.payout < 0:
        current_user.games_lost += 1
    else:
        current_user.games_tied += 1
    
    # Create game history record
    player_hand = ','.join([str(card) for card in game.player_hand.cards])
    dealer_hand = ','.join([str(card) for card in game.dealer_hand.cards])
    
    game_history = GameHistory(
        user_id=current_user.id,
        player_hand=player_hand,
        dealer_hand=dealer_hand,
        bet_amount=game.bet,
        result=game.result,
        profit_loss=game.payout
    )
    
    # Save to database
    db.session.add(game_history)
    db.session.commit()
    
    return jsonify(
        success=True,
        game=session['game'],
        balance=current_user.currency_balance,
        result=game.result,
        payout=game.payout
    )

def game_to_dict(game):
    """Convert game object to dictionary for session storage"""
    return {
        'player_hand': [{'suit': card.suit.value, 'value': card.value, 'is_face_up': card.is_face_up} 
                        for card in game.player_hand.cards],
        'dealer_hand': [{'suit': card.suit.value, 'value': card.value, 'is_face_up': card.is_face_up} 
                        for card in game.dealer_hand.cards],
        'state': game.state.value,
        'bet': game.bet,
        'result': game.result,
        'payout': game.payout
    }

def dict_to_game(game_dict):
    """Convert dictionary to game object from session storage"""
    from blackjack.game.blackjack import BlackjackGame, Hand, Card, Suit, GameState
    
    game = BlackjackGame()
    
    if not game_dict:
        return game
    
    # Restore player hand
    game.player_hand = Hand()
    for card_dict in game_dict.get('player_hand', []):
        card = Card(Suit(card_dict['suit']), card_dict['value'])
        card.is_face_up = card_dict['is_face_up']
        game.player_hand.add_card(card)
    
    # Restore dealer hand
    game.dealer_hand = Hand()
    for card_dict in game_dict.get('dealer_hand', []):
        card = Card(Suit(card_dict['suit']), card_dict['value'])
        card.is_face_up = card_dict['is_face_up']
        game.dealer_hand.add_card(card)
    
    # Restore game state
    game.state = GameState(game_dict.get('state', 'betting'))
    game.bet = game_dict.get('bet', 0)
    game.result = game_dict.get('result', None)
    game.payout = game_dict.get('payout', 0)
    
    return game