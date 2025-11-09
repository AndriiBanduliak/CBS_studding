from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from blackjack.main import main_bp
from blackjack.models import GameHistory, User
from blackjack import db
from blackjack.logger import logger
from blackjack.main.forms import AvatarForm

@main_bp.route('/')
def index():
    return render_template('main/index.html', title='Blackjack Game')

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    avatar_form = AvatarForm()
    if avatar_form.validate_on_submit():
        current_user.avatar = avatar_form.avatar.data
        db.session.commit()
        logger.info(f"Пользователь {current_user.email} изменил аватар на {avatar_form.avatar.data}")
        flash('Аватар успешно обновлен!', 'success')
        return redirect(url_for('main.profile'))
    return render_template('main/profile.html', title='My Profile', user=current_user, 
                          game_history_model=GameHistory, avatar_form=avatar_form)

@main_bp.route('/reset_balance', methods=['POST'])
@login_required
def reset_balance():
    if current_user.email == 'test1@test@gmail.com':
        current_user.currency_balance = 1000
        db.session.commit()
        logger.info(f"Баланс сброшен для мастер-аккаунта {current_user.email}")
        flash('Баланс успешно сброшен до 1000', 'success')
    else:
        logger.warning(f"Попытка сброса баланса от неавторизованного пользователя {current_user.email}")
        flash('Только мастер-аккаунт может сбросить баланс', 'danger')
    return redirect(url_for('main.profile'))

@main_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user_id = current_user.id
    email = current_user.email
    
    # Удаляем историю игр пользователя
    GameHistory.query.filter_by(user_id=user_id).delete()
    
    # Удаляем пользователя
    from flask_login import logout_user
    logout_user()
    
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    
    logger.info(f"Аккаунт удален: {email}")
    flash('Ваш аккаунт был успешно удален', 'success')
    return redirect(url_for('main.index'))