# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    podcasts = db.relationship('Podcast', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Podcast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    rss_feed = db.Column(db.String(500), unique=True, nullable=False)
    category = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    episodes = db.relationship('Episode', backref='podcast', lazy=True)
    analytics = db.relationship('PodcastAnalytics', backref='podcast', lazy=True)

# ... (rest of the models remain the same)

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    publish_date = db.Column(db.DateTime, default=datetime.utcnow)
    podcast_id = db.Column(db.Integer, db.ForeignKey('podcast.id'), nullable=False)
    analytics = db.relationship('EpisodeAnalytics', backref='episode', lazy=True)

class PodcastAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    total_listeners = db.Column(db.Integer, default=0)
    new_listeners = db.Column(db.Integer, default=0)
    podcast_id = db.Column(db.Integer, db.ForeignKey('podcast.id'), nullable=False)

class EpisodeAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    listens = db.Column(db.Integer, default=0)
    unique_listeners = db.Column(db.Integer, default=0)
    episode_id = db.Column(db.Integer, db.ForeignKey('episode.id'), nullable=False)

class SmartLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    destination_url = db.Column(db.String(500), nullable=False)
    podcast_id = db.Column(db.Integer, db.ForeignKey('podcast.id'), nullable=False)
    clicks = db.relationship('SmartLinkClick', backref='smart_link', lazy=True)

class SmartLinkClick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_agent = db.Column(db.String(200))
    ip_address = db.Column(db.String(50))
    referrer = db.Column(db.String(500))
    smart_link_id = db.Column(db.Integer, db.ForeignKey('smart_link.id'), nullable=False)
