# Penn Labs Backend Challenge

## Documentation

### Models

`Club`: Represents a club at Penn. Contains the following fields:

- `id`: Primary key for the club
- `name`: Name of the club (modifiable)
- `code`: Code of the club (modifiable)
- `description`: Description of the club (modifiable)
- `reviews`: One-to-many relationship with `Review` model
- `rating`: Average rating of the club from reviews. If there are no reviews, rating is `null`. Choosing to calculate and store this value in the database for performance reasons. This value is updated whenever a review is added or deleted.
- `favorite_count`: Number of users who have favorited the club. This value is updated whenever a user favorites or unfavorites the club.
- `tags`: Many-to-many relationship with `Tag` model. I don't allow tags to be added to a club after creation, since I assumed that a club won't change much over time in this scenario. This can be modified later.

`User`: Represents a user of the application. Contains the following fields:

- `id`: Primary key for the user
- `username`: Username of the user
- `password`: (hashed) Password of the user
- `favorites`: Many-to-many relationship with `Club` model
- `reviews`: One-to-many relationship with `Review` model

`Review`: Represents a review of a club. Contains the following fields:

- `id`: Primary key for the review
- `club_id`: Foreign key to the `Club` model
- `user_id`: Foreign key to the `User` model
- `date`: DateTime of the review (updates when review is edited via `PUT`)
- `rating`: Rating of the club (1-5) (modifiable)
- `comment`: Comment on the club (modifiable)

`Tag`: Represents a tag that can be associated with a club. Contains the following fields:

- `id`: Primary key for the tag
- `name`: Name of the tag

`ClubTag`: Represents the many-to-many relationship between `Club` and `Tag`. Contains the following fields:

- `club_id`: Foreign key to the `Club` model
- `tag_id`: Foreign key to the `Tag` model

`FavoriteClub`: Represents the many-to-many relationship between `User` and `Club`. Contains the following fields:

- `user_id`: Foreign key to the `User` model
- `club_id`: Foreign key to the `Club` model

### Routes

Note: Ideally, only a user with perms should be able to do some things (like only club officers can modify club details) but have not implemented any sort of administrative hierarchy, so any "logged in" user can do it. But for some user-specific things, like modifying one's own review, only the user who wrote the review can modify it (which they might need to, since users may not review the same club twice).

`/api`: GET route that returns a message indicating that the API is running. The response object contains the following fields:

- `message`: Message indicating that the API is running, "Welcome to the Penn Club Review API!."

`/api/login`: POST route that allows a user to login. The request body should contain the following fields:

- `username`: Username of the user
- `password`: Password of the user

`/api/logout`: POST route that allows a user to logout. User ID automatically extracted from JWT.

`/api/register`: POST route that allows a user to register. The request body should contain the following fields:

- `username`: Username of the user
- `password`: Password of the user

`/api/clubs`: GET route that returns a list of all clubs. Each club object contains the following fields:

- `id`: Primary key for the club
- `name`: Name of the club
- `code`: Code of the club
- `description`: Description of the club
- `rating`: Average rating of the club
- `reviews`: List of reviews associated with the club
- `favorite_count`: Number of users who have favorited the club
- `tags`: List of tags associated with the club

`/api/clubs`: POST route that creates a club. There is no PUT in this route to modify an entire Club, rather there are multiple PUT's for each attribute. The request body should contain the following fields:

- `name`: Name of the club
- `code`: Code of the club
- `description`: Description of the club
- `tags`: List of tags (the name, not ID) associated with the club

`/api/clubs/search/<string:search_query>`: GET route that returns all clubs whose name includes `search_query` (case-insensitive). Each club object contains the following fields:

- `id`: Primary key for the club
- `name`: Name of the club
- `code`: Code of the club
- `description`: Description of the club
- `rating`: Average rating of the club
- `reviews`: List of reviews associated with the club
- `favorite_count`: Number of users who have favorited the club
- `tags`: List of tags associated with the club

`/api/clubs/<int:club_id>`: GET route that returns a specific club. The club object contains the following fields:

- `id`: Primary key for the club
- `name`: Name of the club
- `code`: Code of the club
- `description`: Description of the club
- `rating`: Average rating of the club
- `reviews`: List of reviews associated with the club
- `favorite_count`: Number of users who have favorited the club
- `tags`: List of tags associated with the club

`/api/clubs/<string:club_code>`: GET route that returns a specific club by code. The club object contains the following fields:

- `id`: Primary key for the club
- `name`: Name of the club
- `code`: Code of the club
- `description`: Description of the club
- `rating`: Average rating of the club
- `reviews`: List of reviews associated with the club
- `favorite_count`: Number of users who have favorited the club
- `tags`: List of tags associated with the club

`/api/clubs/<int:club_id>/code`: PUT route that allows a user to update the code of a club. User ID automatically extracted from JWT. The request body should contain the following fields:

- `code`: Code of the club

`/api/clubs/<int:club_id>/name`: GET route that returns the name of a specific club. The name object contains the following fields:

- `name`: Name of the club

`/api/clubs/<int:club_id>/name`: PUT route that allows a user to update the name of a club. User ID automatically extracted from JWT. The request body should contain the following fields:

- `name`: Name of the club

`/api/clubs/<int:club_id>/description`: GET route that returns the description of a specific club. The description object contains the following fields:

- `description`: Description of the club

`/api/clubs/<int:club_id>/description`: PUT route that allows a user to update the description of a club. The request body should contain the following fields:

- `description`: Description of the club

`/api/clubs/<int:club_id>/rating`: GET route that returns the rating of a specific club. The rating object contains the following fields:

- `rating`: Average rating of the club

`/api/clubs/<int:club_id>/reviews`: GET route that returns a list of reviews associated with a club. Each review object contains the following fields:

- `id`: Primary key for the review
- `user_id`: ID of the user
- `rating`: Rating of the club
- `comment`: Comment on the club

`/api/clubs/<int:club_id>/reviews`: POST route that allows a user to add a review to a club. User ID automatically extracted from JWT. The request body should contain the following fields:

- `rating`: Rating of the club
- `comment`: Comment on the club

`/api/clubs/<int:club_id>/tags`: GET route that returns a list of tags associated with a club. Each tag object contains the following fields:

- `id`: Primary key for the tag
- `name`: Name of the tag

`/api/clubs/<int:club_id>/favorite`: POST route that allows a user to add a club to their favorites. User ID automatically extracted from JWT.

`/api/clubs/<int:club_id>/favorite`: DELETE route that allows a user to remove a club from their favorites. User ID automatically extracted from JWT.

`/api/clubs/<int:club_id>/favorite`: GET route that returns all the users who have favorited a club. The favorite object contains the following fields:

- `id`: Primary key for the user
- `username`: Username of the user

`/api/clubs/<int:club_id>/favorite_count`: GET route that returns the number of users who have favorited a club. The favorite_count object contains the following fields:

- `favorite_count`: Number of users who have favorited the club

`/api/users/<int:user_id>`: GET route that returns a specific user. The user object contains the following fields:

- `id`: Primary key for the user
- `username`: Username of the user
- `favorites`: List of club_id's that the user has favorited
- `reviews`: List of review_id's that the user has written

`/api/users/<string:username>`: GET route that returns a specific user by username. The user object contains the following fields:

- `id`: Primary key for the user (or should we not return this, I don't see the security risk? Easy fix if it is...)
- `username`: Username of the user
- `favorites`: List of club_id's that the user has favorited
- `reviews`: List of review_id's that the user has written

`/api/users/<int:user_id>/password`: PUT route that allows a user to update their password, verified using JWT. The request body should contain the following fields:

- `password`: New password for the user

`/api/users/<int:user_id>/username`: GET route that returns the username of a specific user. The username object contains the following fields:

- `username`: Username of the user

`/api/users/<int:user_id>/username`: PUT route that allows a user to update their username. The request body should contain the following fields:

- `username`: Username of the user

`/api/users/<int:user_id>/favorites`: GET route that returns a list of clubs that a user has favorited. Each club object contains the following fields:

- `id`: Primary key for the club
- `name`: Name of the club

`/api/users/<int:user_id>/reviews`: GET route that returns a list of reviews that a user has written. Each review object contains the following fields:

- `id`: Primary key for the review
- `club_id`: ID of the club
- `rating`: Rating of the club
- `comment`: Comment on the club

`/api/tags`: GET route that returns a list of all tags. Each tag object contains the following fields:

- `id`: Primary key for the tag
- `name`: Name of the tag
- `clubs`: List of club_id's that the tag is associated with
- `count`: Number of clubs associated with the tag

`/api/tags/<int:tag_id>`: GET route that returns a specific tag. The tag object contains the following fields:

- `id`: Primary key for the tag
- `name`: Name of the tag
- `clubs`: List of club_id's that the tag is associated with

`/api/tags/<int:tag_id>/clubs`: GET route that returns a list of clubs associated with a specific tag. Each club object contains the following fields:

- `id`: Primary key for the club
- `name`: Name of the club

`/api/tags/<int:tag_id>/clubs_count`: GET route that returns the number of clubs associated with a tag by getting the length of the clubs list. The clubs_count object contains the following fields:

- `clubs_count`: Number of clubs associated with the tag

`/api/tags/<int:tag_id>/name`: GET route that returns the name of a specific tag. The name object contains the following fields:

- `name`: Name of the tag

`/api/reviews`: GET route that returns a list of all reviews. Each review object contains the following fields:

- `id`: Primary key for the review
- `club_id`: ID of the club
- `user_id`: ID of the user
- `date`: DateTime of the review
- `rating`: Rating of the club
- `comment`: Comment on the club

`/api/reviews/<int:review_id>`: GET route that returns a specific review. The review object contains the following fields:

- `id`: Primary key for the review
- `club_id`: ID of the club
- `user_id`: ID of the user
- `date`: DateTime of the review
- `rating`: Rating of the club
- `comment`: Comment on the club

`/api/reviews/<int:review_id>`: DELETE route that allows a user to remove a review. User ID automatically extracted from JWT.

`/api/reviews/<int:review_id>/club_id`: GET route that returns the club_id associated with a specific review. The club object contains the following fields:

- `id`: Primary key for the club
- `name`: Name of the club

`/api/reviews/<int:review_id>/user_id`: GET route that returns the user_id associated with a specific review. The user object contains the following fields:

- `id`: Primary key for the user
- `username`: Username of the user

`/api/reviews/<int:review_id>/content`: GET route that returns the date, rating, and comment of a specific review. The rating object contains the following fields:

- `date`: DateTime of the review
- `rating`: Rating of the club
- `comment`: Comment on the club

`/api/reviews/<int:review_id>/content`: PUT route that allows a user to update the rating and/or comment of a review. The date is automatically updated to the time it is edited. User ID automatically extracted from JWT. The request body should contain the following fields:

- `rating`: Rating of the club
- `comment`: Comment on the club

## Installation

1. Click the green "use this template" button to make your own copy of this repository, and clone it. Make sure to create a **private repository**.
2. Change directory into the cloned repository.
3. Install `pipx`
   - `brew install pipx` (macOS)
   - See instructions here https://github.com/pypa/pipx for other operating systems
4. Install `poetry`
   - `pipx install poetry`
5. Install packages using `poetry install`.

## File Structure

- `app.py`: Main file. Has configuration and setup at the top. Add your [URL routes](https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing) to this file!
- `models.py`: Model definitions for SQLAlchemy database models. Check out documentation on [declaring models](https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/) as well as the [SQLAlchemy quickstart](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#quickstart) for guidance
- `bootstrap.py`: Code for creating and populating your local database. You will be adding code in this file to load the provided `clubs.json` file into a database.

## Developing

0. Determine how to model the data contained within `clubs.json` and then complete `bootstrap.py`
1. Activate the Poetry shell with `poetry shell`.
2. Run `python3 bootstrap.py` to create the database and populate it.
3. Use `flask run` to run the project.
4. Follow the instructions [here](https://www.notion.so/pennlabs/Backend-Challenge-862656cb8b7048db95aaa4e2935b77e5).
5. Document your work in this `README.md` file.

## Submitting

Follow the instructions on the Technical Challenge page for submission.

## Installing Additional Packages

Use any tools you think are relevant to the challenge! To install additional packages
run `poetry add <package_name>` within the directory. Make sure to document your additions.
