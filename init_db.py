# init_db.py
from app import app, db
from models import User, Podcast, Episode, PodcastAnalytics, EpisodeAnalytics, SmartLink, SmartLinkClick

def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created.")

if __name__ == "__main__":
    init_db()
