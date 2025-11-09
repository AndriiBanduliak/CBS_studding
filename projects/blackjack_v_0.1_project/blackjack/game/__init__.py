from flask import Blueprint

game_bp = Blueprint('game', __name__, url_prefix='/game')

from blackjack.game import routes