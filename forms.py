# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError, URL

# Try to import Email validator, use a custom validator if not available
try:
    from wtforms.validators import Email
except ImportError:
    from wtforms.validators import Regexp
    import re
    
    class Email(Regexp):
        def __init__(self, message=None):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            super().__init__(pattern, re.IGNORECASE, message or 'Invalid email address.')

from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class PodcastForm(FlaskForm):
    rss_feed = StringField('RSS Feed URL', validators=[DataRequired(), URL()])
    category = SelectField('Category', choices=[
        ('Comedy', 'Comedy'),
        ('News', 'News'),
        ('Technology', 'Technology'),
        ('Business', 'Business'),
        ('Education', 'Education'),
        ('Entertainment', 'Entertainment'),
        ('Politics', 'Politics'),
        ('Sports', 'Sports'),
        ('True Crime', 'True Crime'),
        ('Other', 'Other')
    ])
    submit = SubmitField('Add Podcast')

class SmartLinkForm(FlaskForm):
    destination_url = StringField('Destination URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Create SmartLink')
