from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import praw

# Flask app setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reddit_quest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Reddit API setup
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="Reddit Quest Game",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD"
)

# Database Models
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    progress = db.Column(db.Integer, default=0)

# Initialize database
db.create_all()

# Clues Data
clues = [
    {
        "clue": "I'm a place where pixels thrive, but only one every five.",
        "subreddit": "place",
        "validation": "Visit the pinned post and find the phrase 'Pixel Power'"
    },
    {
        "clue": "Where tales are told in six words, find the golden bird.",
        "subreddit": "sixwordstories",
        "validation": "Comment 'Found it!' on the post titled 'Golden Bird Story'."
    }
]

# API Routes
@app.route('/api/get_clue', methods=['POST'])
def get_clue():
    username = request.json.get('username')

    if not username:
        return jsonify({"error": "Username is required."}), 400

    player = Player.query.filter_by(username=username).first()
    if not player:
        player = Player(username=username, progress=0)
        db.session.add(player)
        db.session.commit()

    progress = player.progress
    if progress >= len(clues):
        return jsonify({"message": "Congratulations! You've completed the quest."})

    return jsonify({"clue": clues[progress]["clue"]})

@app.route('/api/submit_progress', methods=['POST'])
def submit_progress():
    username = request.json.get('username')
    subreddit = request.json.get('subreddit')
    action = request.json.get('action')

    if not username or not subreddit or not action:
        return jsonify({"error": "All fields are required."}), 400

    player = Player.query.filter_by(username=username).first()
    if not player:
        return jsonify({"error": "Player not found."}), 404

    progress = player.progress

    if progress >= len(clues):
        return jsonify({"message": "You've already completed the quest!"})

    expected_subreddit = clues[progress]['subreddit']
    if subreddit.lower() != expected_subreddit.lower():
        return jsonify({"error": f"Incorrect subreddit! Try {expected_subreddit}."}), 400

    # Simple validation for demo purposes
    if action.lower() in clues[progress]['validation'].lower():
        player.progress += 1
        db.session.commit()
        return jsonify({"message": "Correct! Here's your next clue:", "clue": clues[player.progress]["clue"] if player.progress < len(clues) else "Quest Completed!"})

    return jsonify({"error": "Incorrect action. Please try again."}), 400

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)