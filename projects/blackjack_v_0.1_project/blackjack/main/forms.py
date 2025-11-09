from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

class AvatarForm(FlaskForm):
    avatar = SelectField('Выберите аватар', choices=[
        ('default.png', 'По умолчанию'),
        ('smile.png', 'Улыбка'),
        ('cool.png', 'Крутой'),
        ('happy.png', 'Счастливый'),
        ('wink.png', 'Подмигивающий'),
        ('laugh.png', 'Смеющийся')
    ])
    submit = SubmitField('Сохранить')