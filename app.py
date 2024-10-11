# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from urllib.parse import urlparse
from models import db, User, Podcast, Episode, PodcastAnalytics, EpisodeAnalytics, SmartLink, SmartLinkClick
from forms import LoginForm, RegistrationForm, PodcastForm, SmartLinkForm
import feedparser
from datetime import datetime, timedelta
import random
import string
import csv
import os
from sqlalchemy.exc import IntegrityError


# app.py
# ... (previous imports)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///podcasts_new.db'  # Changed to a new database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def load_top_podcasts():
    top_podcasts = []
    with open('top_podcasts.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            top_podcasts.append(row)
    return top_podcasts




db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

from flask import request, flash, redirect, url_for
from flask_login import login_required, current_user

@app.route('/add_podcast', methods=['GET', 'POST'])
@login_required
def add_podcast():
    form = PodcastForm()
    if form.validate_on_submit():
        # Check if the podcast already exists
        existing_podcast = Podcast.query.filter_by(rss_feed=form.rss_feed.data).first()
        if existing_podcast:
            flash('This podcast has already been added.', 'warning')
        else:
            feed = feedparser.parse(form.rss_feed.data)
            podcast = Podcast(
                title=feed.feed.get('title', 'Unknown Title'),
                author=feed.feed.get('author', 'Unknown Author'),
                rss_feed=form.rss_feed.data,
                category=form.category.data,
                user_id=current_user.id
            )
            db.session.add(podcast)
            
            for entry in feed.entries:
                episode = Episode(
                    title=entry.get('title', 'Unknown Episode'),
                    publish_date=datetime(*entry.get('published_parsed', datetime.now().timetuple())[:6]),
                    podcast_id=podcast.id
                )
                db.session.add(episode)
            
            try:
                db.session.commit()
                flash('Podcast added successfully!', 'success')
                return redirect(url_for('dashboard'))
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred while adding the podcast. Please try again.', 'error')

    top_podcasts = load_top_podcasts()
    return render_template('add_podcast.html', form=form, top_podcasts=top_podcasts)






PODCAST_RSS_FEEDS = {
    "Joe Rogan Experience Review podcast": "https://feeds.megaphone.fm/HSW9425354773",
    "Crime Junkie": "https://feeds.megaphone.fm/CAD173560212",
    "Stuff You Should Know": "https://feeds.megaphone.fm/HSW9867626005",
    "Call Her Daddy": "https://rss.art19.com/call-her-daddy",
    "The Daily": "https://feeds.simplecast.com/54nAGcIl",
    "TED Talks Daily": "https://feeds.npr.org/tedtalksdaily/podcast.xml",
    "The Joe Rogan Experience": "https://joeroganexp.libsyn.com/rss",
    "The Michelle Obama Podcast": "https://rss.art19.com/the-michelle-obama-podcast",
    "Freakonomics Radio": "https://feeds.feedburner.com/freakonomicsradio",
    "The Dave Ramsey Show": "https://feeds.ramseysolutions.com/BWU8",
    "The Ben Shapiro Show": "https://feeds.megaphone.fm/TQC7170300919",
    "How I Built This with Guy Raz": "https://feeds.npr.org/510313/podcast.xml",
    "Armchair Expert with Dax Shepard": "https://feeds.simplecast.com/REn_Jec8",
    "Pod Save America": "https://feeds.megaphone.fm/ADL8579940144",
    "The Tim Ferriss Show": "https://rss.art19.com/tim-ferriss-show",
    "Planet Money": "https://feeds.npr.org/510289/podcast.xml",
    "The Tony Robbins Podcast": "https://tonyrobbins.libsyn.com/rss",
    "The Happiness Lab with Dr. Laurie Santos": "https://feeds.megaphone.fm/SM5713621638",
    "The Rachel Maddow Show": "https://feeds.megaphone.fm/NBC2001149817",
    "The Peter Attia Drive": "https://peterattiamd.libsyn.com/rss",
    "The Jordan B. Peterson Podcast": "https://feeds.libsyn.com/178048/rss",
    "TED Radio Hour": "https://feeds.npr.org/510298/podcast.xml",
    "The Rich Roll Podcast": "https://richroll.libsyn.com/rss",
    "The Mindset Mentor": "https://feeds.simplecast.com/mSOI3dUz",
    "The Doctor's Farmacy with Mark Hyman, MD": "https://drhyman.libsyn.com/rss",
    "The Minimalists Podcast": "https://feeds.simplecast.com/lIV9mhTG",
    "WorkLife with Adam Grant": "https://feeds.simplecast.com/Si5WfGMz",
    "Unlocking Us with Brené Brown": "https://feeds.simplecast.com/VJ43v3BG",
    "The History Extra podcast": "https://rss.acast.com/historyextra",
    "The Happiness Project": "https://feeds.buzzsprout.com/846579.rss",
    "The Art of Charm": "https://feeds.megaphone.fm/TAOC4160734043",
    "Oprah's SuperSoul Conversations": "https://feeds.simplecast.com/dI8fBIXH",
    "The Daily Stoic": "https://thedailystoic.libsyn.com/rss",
    "Call Me Candid": "https://feeds.buzzsprout.com/862646.rss",
    "The Ed Mylett Show": "https://feeds.simplecast.com/TzA03c2U",
    "My Favorite Murder": "https://feeds.megaphone.fm/HSW7229313235",
    "Serial": "https://serialpodcast.org/rss",
    "Conan O’Brien Needs A Friend": "https://feeds.megaphone.fm/HSW8064721387",
    "On Purpose with Jay Shetty": "https://feeds.simplecast.com/wAGpNgdw",
    "The Bill Simmons Podcast": "https://rss.art19.com/the-bill-simmons-podcast",
    "SmartLess": "https://feeds.megaphone.fm/SLT4802050387",
    "The Breakfast Club": "https://feeds.megaphone.fm/WWO4121502095",
    "The Indicator from Planet Money": "https://feeds.npr.org/510325/podcast.xml",
    "The Matt Walsh Show": "https://feeds.megaphone.fm/TQC7193760306",
    "Radiolab": "https://feeds.wnyc.org/radiolab",
    "The Moth": "https://feeds.themoth.org/themothpodcast",
    "The Daily Wire Backstage": "https://feeds.megaphone.fm/TQC6689336247",
    "The Glenn Beck Program": "https://feeds.megaphone.fm/ADL5713510324",
    "The Happiness Equation": "https://feeds.simplecast.com/xV3z8k3A",
    "Pardon My Take": "https://pardon-my-take.simplecast.com/rss",
    "RedHanded": "https://feeds.acast.com/public/shows/5b5465cb438b7297156bc5e2",
    "This American Life": "https://feeds.thisamericanlife.org/talpodcast",
    "The Jordan Harbinger Show": "https://feeds.megaphone.fm/ADL7231845163",
    "Science Vs": "https://feeds.megaphone.fm/ADL1789470748",
    "The Daily Zeitgeist": "https://feeds.megaphone.fm/DLG5461127480",
    "Wait Wait... Don't Tell Me!": "https://feeds.npr.org/35/podcast.xml",
    "Song Exploder": "https://feeds.feedburner.com/SongExploder",
    "The Last Podcast on the Left": "https://feeds.megaphone.fm/LPO8334067017",
    "The Office Ladies": "https://feeds.megaphone.fm/HSW4937616783",
    "Comedy Bang Bang": "https://feeds.megaphone.fm/WIT6241047387",
    "The Sporkful": "https://feeds.megaphone.fm/STP7760570953",
    "Doughboys": "https://feeds.megaphone.fm/WIN6979397485",
    "The Fantasy Footballers Podcast": "https://rss.art19.com/the-fantasy-footballers-podcast",
    "The Lowe Post": "https://rss.art19.com/the-lowe-post",
    "A Podcast to the Past": "https://feeds.buzzsprout.com/952675.rss",
    "The Adam and Dr. Drew Show": "https://adamanddrdrewshow.libsyn.com/rss",
    "Your Mom’s House": "https://rss.art19.com/your-moms-house",
    "Stuff They Don't Want You to Know": "https://feeds.megaphone.fm/HSW2089233327",
    "The Breakfast Club": "https://feeds.megaphone.fm/WWO4121502095",
    "The Ezra Klein Show": "https://feeds.simplecast.com/Yh2axj2I",
    "Planet Money": "https://feeds.npr.org/510289/podcast.xml",
    "The Knowledge Project": "https://theknowledgeproject.libsyn.com/rss",
    "Philosophize This!": "https://philosophizethis.libsyn.com/rss",
    "Side Hustle School": "https://feeds.megaphone.fm/side-hustle-school",
    "The Infinite Monkey Cage": "https://www.bbc.co.uk/programmes/p02pc9jj/episodes/downloads.rss",
    "Hidden Brain": "https://feeds.npr.org/510308/podcast.xml",
    "The Tony Robbins Podcast": "https://tonyrobbins.libsyn.com/rss",
    "Planet Money": "https://feeds.npr.org/510289/podcast.xml",
    "Revolutions": "https://revolutionspodcast.libsyn.com/rss",
    "Against the Rules with Michael Lewis": "https://feeds.megaphone.fm/RTL1049561987",
    "Dax Shepard's Armchair Expert": "https://feeds.simplecast.com/REn_Jec8",
    "Rationally Speaking": "https://rationallyspeakingpodcast.libsyn.com/rss",
    "The Daily Boost": "https://dailyboost.libsyn.com/rss",
    "The Minimalists Podcast": "https://feeds.simplecast.com/lIV9mhTG",
    "The Doctor's Farmacy": "https://drhyman.libsyn.com/rss"
}


@app.route('/dashboard')
@login_required
def dashboard():
    user_podcasts = Podcast.query.filter_by(user_id=current_user.id).all()
    top_podcasts = load_top_podcasts()
    return render_template('dashboard.html', user_podcasts=user_podcasts, top_podcasts=top_podcasts[:100])

@app.route('/search_podcasts')
def search_podcasts():
    query = request.args.get('q', '').lower()
    top_podcasts = load_top_podcasts()
    results = [podcast for podcast in top_podcasts if query in podcast['title'].lower() or query in podcast['author'].lower()]
    return jsonify(results[:10])


@app.route('/podcast/<int:id>')
@login_required
def podcast_detail(id):
    podcast = Podcast.query.get_or_404(id)
    if podcast.user_id != current_user.id:
        flash('You do not have permission to view this podcast.')
        return redirect(url_for('dashboard'))
    
    # Generate some mock data for demonstration
    dates = [datetime.now().date() - timedelta(days=x) for x in range(30)]
    total_listeners = [random.randint(1000, 5000) for _ in range(30)]
    new_listeners = [random.randint(100, 500) for _ in range(30)]
    
    return render_template('podcast_detail.html', podcast=podcast, dates=dates, total_listeners=total_listeners, new_listeners=new_listeners)

@app.route('/create_smartlink/<int:podcast_id>', methods=['GET', 'POST'])
@login_required
def create_smartlink(podcast_id):
    podcast = Podcast.query.get_or_404(podcast_id)
    if podcast.user_id != current_user.id:
        flash('You do not have permission to create a SmartLink for this podcast.')
        return redirect(url_for('dashboard'))
    
    form = SmartLinkForm()
    if form.validate_on_submit():
        short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        smart_link = SmartLink(
            short_code=short_code,
            destination_url=form.destination_url.data,
            podcast_id=podcast.id
        )
        db.session.add(smart_link)
        db.session.commit()
        flash(f'SmartLink created: {request.host_url}s/{short_code}')
        return redirect(url_for('podcast_detail', id=podcast.id))
    return render_template('create_smartlink.html', form=form, podcast=podcast)

@app.route('/s/<short_code>')
def smart_link_redirect(short_code):
    smart_link = SmartLink.query.filter_by(short_code=short_code).first_or_404()
    click = SmartLinkClick(
        user_agent=request.user_agent.string,
        ip_address=request.remote_addr,
        referrer=request.referrer,
        smart_link_id=smart_link.id
    )
    db.session.add(click)
    db.session.commit()
    return redirect(smart_link.destination_url)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)