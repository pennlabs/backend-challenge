from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from functools import wraps

DB_FILE = "clubreview.db"

# Database configuration and app initialization
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
app.config["JWT_SECRET_KEY"] = "supersecretkey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600 # 1hr for testing lol

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

from models import *

# Validation helpers
def validate_rating(rating):
    """Validate rating is an integer between 1 and 5"""
    if not isinstance(rating, int):
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            return False
    return 1 <= rating <= 5

def validate_string_field(field, min_length=1, max_length=255):
    """Validate string field length and type"""
    return isinstance(field, str) and min_length <= len(field) <= max_length

def requires_json_data(f):
    """Decorator to validate JSON request data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        return f(*args, **kwargs)
    return decorated_function

# Base routes
@app.route("/")
def main():
    """Base endpoint returning welcome message"""
    return "Welcome to Penn Club Review!"

@app.route("/api")
def api():
    """API base endpoint"""
    return jsonify({"message": "Welcome to the Penn Club Review API!."})

# Authentication routes / Session management
@app.route("/api/register", methods=["POST"])
@requires_json_data
def register():
    """Register new user with username and password"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not validate_string_field(username, max_length=80):
        return jsonify({"error": "Invalid username. Must be 1-80 characters"}), 400
    if not password or not validate_string_field(password, min_length=6, max_length=128):
        return jsonify({"error": "Invalid password. Must be 6-128 characters"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/api/login", methods=["POST"])
@requires_json_data
def login():
    """Authenticate user and return JWT token"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401
    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token}), 200

@app.route("/api/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout user (stateless with JWT)"""
    # since JWT is stateless, we just return success
    # in a real app, you might want to blacklist the token
    return jsonify({"message": "Successfully logged out"}), 200

# Club routes - Main operations
@app.route("/api/clubs", methods=["GET", "POST"])
def manage_clubs():
    """Get all clubs or create a new club"""
    if request.method == "GET":
        clubs = Club.query.all()
        return jsonify([{
            "id": club.id, 
            "name": club.name, 
            "code": club.code, 
            "description": club.description,
            "rating": club.rating, 
            "favorite_count": club.favorite_count, 
            "tags": [tag.name for tag in club.tags],
            "reviews": [{
                "id": review.id, 
                "user_id": review.user_id, 
                "rating": review.rating, 
                "comment": review.comment
            } for review in club.reviews]
        } for club in clubs])
    if request.method == "POST":
        @jwt_required()
        @requires_json_data
        def create_club():
            data = request.get_json()
            # Validate required fields
            name = data.get("name")
            code = data.get("code")
            description = data.get("description", "")
            tags = data.get("tags", [])
            if not name or not validate_string_field(name):
                return jsonify({"error": "Invalid name. Must be 1-255 characters"}), 400
            if not code or not validate_string_field(code):
                return jsonify({"error": "Invalid code. Must be 1-255 characters"}), 400
            if description and not validate_string_field(description, max_length=1000):
                return jsonify({"error": "Description must be less than 1000 characters"}), 400
            if not isinstance(tags, list):
                return jsonify({"error": "Tags must be a list of strings"}), 400
            # Check if club code already exists
            if Club.query.filter_by(code=code).first():
                return jsonify({"error": "Club code already exists"}), 409
            # Create new club
            new_club = Club(
                name=name,
                code=code,
                description=description
            )
            # Handle tags
            for tag_name in tags:
                if not validate_string_field(tag_name, max_length=80):
                    return jsonify({"error": f"Invalid tag name: {tag_name}"}), 400
                # Get existing tag or create new one
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                new_club.tags.append(tag)
            db.session.add(new_club)
            db.session.commit()
            return jsonify({
                "message": "Club created successfully",
                "club": {
                    "id": new_club.id,
                    "name": new_club.name,
                    "code": new_club.code,
                    "description": new_club.description,
                    "tags": [tag.name for tag in new_club.tags]
                }
            }), 201
        return create_club()

@app.route("/api/clubs/search/<string:search_query>", methods=["GET"])
def search_clubs(search_query):
    """Search clubs by name (case-insensitive)"""
    clubs = Club.query.filter(Club.name.ilike(f"%{search_query}%")).all()
    return jsonify([{
        "id": club.id, 
        "name": club.name, 
        "code": club.code, 
        "description": club.description,
        "rating": club.rating, 
        "favorite_count": club.favorite_count, 
        "tags": [tag.name for tag in club.tags],
        "reviews": [{
            "id": review.id, 
            "user_id": review.user_id, 
            "rating": review.rating, 
            "comment": review.comment
        } for review in club.reviews]
    } for club in clubs])

# Club routes - Individual club operations
@app.route("/api/clubs/<int:club_id>", methods=["GET"])
def get_club(club_id):
    """Get specific club by ID"""
    club = Club.query.get_or_404(club_id)
    return jsonify({
        "id": club.id,
        "name": club.name,
        "code": club.code,
        "description": club.description,
        "rating": club.rating,
        "favorite_count": club.favorite_count,
        "tags": [tag.name for tag in club.tags],
        "reviews": [{
            "id": review.id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.comment
        } for review in club.reviews]
    })

@app.route("/api/clubs/<string:club_code>", methods=["GET"])
def get_club_by_code(club_code):
    """Get specific club by code"""
    club = Club.query.filter_by(code=club_code).first_or_404()
    return jsonify({
        "id": club.id,
        "name": club.name,
        "code": club.code,
        "description": club.description,
        "rating": club.rating,
        "favorite_count": club.favorite_count,
        "tags": [tag.name for tag in club.tags],
        "reviews": [{
            "id": review.id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.comment
        } for review in club.reviews]
    })

# Club routes - Property operations
@app.route("/api/clubs/<int:club_id>/code", methods=["PUT"])
@jwt_required()
@requires_json_data
def update_club_code(club_id):
    """Update club code (requires authentication)"""
    club = Club.query.get_or_404(club_id)
    data = request.get_json()
    code = data.get("code")
    if not code or not validate_string_field(code):
        return jsonify({"error": "Invalid code. Must be 1-255 characters"}), 400
    # Check if code already exists
    existing_club = Club.query.filter_by(code=code).first()
    if existing_club and existing_club.id != club_id:
        return jsonify({"error": "Club code already exists"}), 409
    club.code = data.get("code")
    db.session.commit()
    return jsonify({"message": "Club code updated successfully"})

@app.route("/api/clubs/<int:club_id>/name", methods=["GET", "PUT"])
def manage_club_name(club_id):
    """Get or update club name"""
    if request.method == "GET":
        club = Club.query.get_or_404(club_id)
        return jsonify({"name": club.name})
    if request.method == "PUT":
        @jwt_required()
        @requires_json_data
        def put_name():
            club = Club.query.get_or_404(club_id)
            data = request.get_json()
            name = data.get("name")
            if not name or not validate_string_field(name):
                return jsonify({"error": "Invalid name. Must be 1-255 characters"}), 400
            if not data or "name" not in data:
                return jsonify({"error": "Name is required"}), 400
            club.name = data["name"]
            db.session.commit()
            return jsonify({"message": "Club name updated successfully"})
        return put_name()

@app.route("/api/clubs/<int:club_id>/description", methods=["GET", "PUT"])
def manage_club_description(club_id):
    """Get or update club description"""
    if request.method == "GET":
        club = Club.query.get_or_404(club_id)
        return jsonify({"description": club.description})
    if request.method == "PUT":
        @jwt_required()
        @requires_json_data
        def put_description():
            club = Club.query.get_or_404(club_id)
            data = request.get_json()
            description = data.get("description")
            if description is not None and not validate_string_field(description, max_length=1000):
                return jsonify({"error": "Description must be less than 1000 characters"}), 400
            if not data or "description" not in data:
                return jsonify({"error": "Description is required"}), 400
            club.description = data["description"]
            db.session.commit()
            return jsonify({"message": "Club description updated successfully"})
        return put_description()

# Club routes - Reviews and ratings
def update_club_rating(club_id):
    """Helper function to update club rating"""
    club = Club.query.get(club_id)
    if not club:
        return
    reviews = club.reviews
    if not reviews:
        club.rating = None
    else:
        club.rating = round(sum(r.rating for r in reviews) / len(reviews), 2)
    db.session.commit()

@app.route("/api/clubs/<int:club_id>/reviews", methods=["GET", "POST"])
def manage_club_reviews(club_id):
    """Get all reviews or add new review for a club. To edit a review, see `/api/reviews/<int:review_id>/content`"""
    if request.method == "GET":
        club = Club.query.get_or_404(club_id)
        return jsonify([{
            "id": review.id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.comment
        } for review in club.reviews])
    if request.method == "POST":
        @jwt_required()
        @requires_json_data
        def post_review():
            data = request.get_json()
            user_id = get_jwt_identity()
            club = Club.query.get(club_id)
            if not club:
                return jsonify({"error": "Club not found"}), 404
            try:
                rating = int(data.get("rating"))
            except (TypeError, ValueError):
                return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
            if not validate_rating(rating):
                return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
            comment = data.get("comment")
            if comment and not validate_string_field(comment, max_length=1000):
                return jsonify({"error": "Comment must be less than 1000 characters"}), 400  
            # Check if user already reviewed this club
            existing_review = Review.query.filter_by(club_id=club_id, user_id=user_id).first()
            if existing_review:
                return jsonify({"error": "User has already reviewed this club"}), 409
            new_review = Review(club_id=club_id, user_id=user_id, rating=rating, comment=comment)
            db.session.add(new_review)
            db.session.commit()
            # Update club rating after adding review
            update_club_rating(club_id)
            return jsonify({"message": "Review added successfully"}), 201
        return post_review()

@app.route("/api/clubs/<int:club_id>/rating", methods=["GET"])
def get_club_rating(club_id):
    """Get club's average rating"""
    club = Club.query.get_or_404(club_id)
    return jsonify({"rating": club.rating})

@app.route("/api/clubs/<int:club_id>/tags", methods=["GET"])
def get_club_tags(club_id):
    """Get club's tags"""
    club = Club.query.get_or_404(club_id)
    return jsonify([{"id": tag.id, "name": tag.name} for tag in club.tags])

# Club routes - Favorites management
@app.route("/api/clubs/<int:club_id>/favorite", methods=["POST", "DELETE", "GET"])
def manage_favorite(club_id):
    """Add/remove/get favorites for a club"""
    if request.method == "GET":
        club = Club.query.get_or_404(club_id)
        return jsonify([{"id": user.id, "username": user.username} for user in club.favorited_by])
    @jwt_required()
    def modify_favorite():
        user_id = get_jwt_identity()
        club = Club.query.get_or_404(club_id)
        user = User.query.get_or_404(user_id)
        if request.method == "POST":
            if club not in user.favorites:
                user.favorites.append(club)
                club.favorite_count += 1
                db.session.commit()
                return jsonify({"message": "Club added to favorites"})
            else:
                return jsonify({"message": "Club already in favorites"})
        if request.method == "DELETE":
            if club in user.favorites:
                user.favorites.remove(club)
                club.favorite_count -= 1
                db.session.commit()
            return jsonify({"message": "Club removed from favorites"})
    return modify_favorite()

@app.route("/api/clubs/<int:club_id>/favorite_count", methods=["GET"])
def get_favorite_count(club_id):
    """Get favorite count for a club"""
    club = Club.query.get_or_404(club_id)
    return jsonify({"favorite_count": club.favorite_count})

# Review routes
@app.route("/api/reviews", methods=["GET"])
def get_reviews():
    """Get all reviews in the system"""
    reviews = Review.query.all()
    return jsonify([{
        "id": review.id,
        "club_id": review.club_id,
        "user_id": review.user_id,
        "date": review.date,
        "rating": review.rating,
        "comment": review.comment
    } for review in reviews])

@app.route("/api/reviews/<int:review_id>", methods=["GET", "DELETE"])
def manage_review(review_id):
    """Get or delete specific review"""
    if request.method == "GET":
        review = Review.query.get_or_404(review_id)
        return jsonify({
            "id": review.id,
            "club_id": review.club_id,
            "user_id": review.user_id,
            "date": review.date,
            "rating": review.rating,
            "comment": review.comment
        })
    if request.method == "DELETE":
        @jwt_required()
        def delete_review():
            user_id = get_jwt_identity()
            review = Review.query.get_or_404(review_id)
            if review.user_id != int(user_id):
                return jsonify({"error": "Unauthorized"}), 403
            club_id = review.club_id
            db.session.delete(review)
            db.session.commit()
            # Update club rating after deleting review
            update_club_rating(club_id)
            return jsonify({"message": "Review deleted successfully"})  
        return delete_review()

@app.route("/api/reviews/<int:review_id>/club_id", methods=["GET"])
def get_review_club_id(review_id):
    """Get club ID associated with a specific review"""
    review = Review.query.get_or_404(review_id)
    return jsonify({"club_id": review.club_id})

@app.route("/api/reviews/<int:review_id>/user_id", methods=["GET"])
def get_review_user_id(review_id):
    """Get user ID associated with a specific review"""
    review = Review.query.get_or_404(review_id)
    return jsonify({"user_id": review.user_id})

@app.route("/api/reviews/<int:review_id>/content", methods=["PUT", "GET"])
def manage_review_content(review_id):
    """Get or update review content"""
    if request.method == "GET":
        review = Review.query.get_or_404(review_id)
        return jsonify({
            "date": review.date,
            "rating": review.rating,
            "comment": review.comment
        })
    if request.method == "PUT":
        @jwt_required()
        @requires_json_data
        def put_review():
            user_id = get_jwt_identity()
            review = Review.query.get_or_404(review_id)
            print(user_id, review.user_id)
            if review.user_id != int(user_id):
                return jsonify({"error": "Unauthorized"}), 403
            data = request.get_json()
            modified = False
            if "rating" in data:
                try:
                    rating = int(data["rating"])
                except (TypeError, ValueError):
                    return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
                if not validate_rating(rating):
                    return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
                review.rating = rating
                modified = True
            if "comment" in data:
                if not validate_string_field(data["comment"], max_length=1000):
                    return jsonify({"error": "Comment must be less than 1000 characters"}), 400
                review.comment = data["comment"]
                modified = True
            if modified:
                db.session.commit()
                # Update club rating after modifying review
                update_club_rating(review.club_id)
            return jsonify({"message": "Review updated successfully"})
        return put_review()

# Tag routes
@app.route("/api/tags", methods=["GET"])
def get_tags():
    """Get all tags with their associated clubs and count"""
    tags = Tag.query.all()
    return jsonify([{
        "id": tag.id,
        "name": tag.name,
        "clubs": [club.id for club in tag.clubs],
        "count": len(tag.clubs)
    } for tag in tags])

@app.route("/api/tags/<int:tag_id>", methods=["GET"])
def get_tag(tag_id):
    """Get specific tag details"""
    tag = Tag.query.get_or_404(tag_id)
    return jsonify({
        "id": tag.id,
        "name": tag.name,
        "clubs": [club.id for club in tag.clubs]
    })

@app.route("/api/tags/<int:tag_id>/name", methods=["GET"])
def get_tag_name(tag_id):
    """Get tag name by ID"""
    tag = Tag.query.get_or_404(tag_id)
    return jsonify({"name": tag.name})

@app.route("/api/tags/<int:tag_id>/clubs", methods=["GET"])
def get_tag_clubs(tag_id):
    """Get clubs associated with a specific tag"""
    tag = Tag.query.get_or_404(tag_id)
    return jsonify([{
        "id": club.id,
        "name": club.name
    } for club in tag.clubs])

@app.route("/api/tags/<int:tag_id>/clubs_count", methods=["GET"])
def get_tag_clubs_count(tag_id):
    """Get count of clubs associated with a specific tag"""
    tag = Tag.query.get_or_404(tag_id)
    return jsonify({"clubs_count": len(tag.clubs)})

# User routes
@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get user details by ID"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "favorites": [club.id for club in user.favorites],
        "reviews": [review.id for review in user.reviews]
    })

@app.route("/api/users/<string:username>", methods=["GET"])
def get_user_by_username(username):
    """Get user details by username"""
    user = User.query.filter_by(username=username).first_or_404()
    return jsonify({
        "id": user.id,
        "username": user.username,
        "favorites": [club.id for club in user.favorites],
        "reviews": [review.id for review in user.reviews]
    })

@app.route("/api/users/<int:user_id>/username", methods=["GET", "PUT"])
def manage_username(user_id):
    """Get or update user's username"""
    if request.method == "GET":
        user = User.query.get_or_404(user_id)
        return jsonify({"username": user.username})
    if request.method == "PUT":
        @jwt_required()
        @requires_json_data
        def put_username():
            user = User.query.get_or_404(user_id)
            if user.id != int(get_jwt_identity()):
                return jsonify({"error": "Unauthorized"}), 403
            data = request.get_json()
            username = data.get("username")
            if not username or not validate_string_field(username, max_length=80):
                return jsonify({"error": "Invalid username. Must be 1-80 characters"}), 400
            if User.query.filter_by(username=username).first():
                return jsonify({"error": "Username already exists"}), 409
            user.username = username
            db.session.commit()
            return jsonify({"message": "Username updated successfully"})
        return put_username()

@app.route("/api/users/<int:user_id>/password", methods=["PUT"])
@jwt_required()
@requires_json_data
def update_password(user_id):
    """Update user's password"""
    user = User.query.get_or_404(user_id)
    if user.id != int(get_jwt_identity()):
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    password = data.get("password")
    if not password or not validate_string_field(password, min_length=6, max_length=128):
        return jsonify({"error": "Invalid password. Must be 6-128 characters"}), 400
    user.password = bcrypt.generate_password_hash(password).decode("utf-8")
    db.session.commit()
    return jsonify({"message": "Password updated successfully"})

@app.route("/api/users/<int:user_id>/favorites", methods=["GET"])
def get_user_favorites(user_id):
    """Get user's favorite clubs"""
    user = User.query.get_or_404(user_id)
    return jsonify([{"id": club.id, "name": club.name} for club in user.favorites])

@app.route("/api/users/<int:user_id>/reviews", methods=["GET"])
def get_user_reviews(user_id):
    """Get all reviews by a specific user"""
    user = User.query.get_or_404(user_id)
    return jsonify([{
        "id": review.id,
        "club_id": review.club_id,
        "rating": review.rating,
        "comment": review.comment
    } for review in user.reviews])

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({"error": "Forbidden"}), 403

if __name__ == "__main__":
    app.run()