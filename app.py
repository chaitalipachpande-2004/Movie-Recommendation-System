import sqlite3
from flask import Flask, render_template, request , session , redirect
import pickle
from datetime import datetime

from model.hybrid_recommender import (
    content_recommend,
    collaborative_recommend,
    hybrid_recommend
)

app = Flask(__name__)

app.secret_key = "movie_recommender_secret_key"

# Load movie names for dropdown suggestions
movies = pickle.load(
    open('model/saved_models/movies.pkl', 'rb')
)

movie_list = sorted(
    movies['title'].tolist()
)


@app.route('/')
def home():
    return render_template(
        'home.html',
        movies=movie_list
    )


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(
            'database/movie_recommendation.db'
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE username = ?
            AND password = ?
            """,
            (username, password)
        )
       

        user = cursor.fetchone()

        conn.close()

        if user:

            session['user_id'] = user [0]
            session['username'] = user[1]

            return f"""
            <h2 style='text-align:center;margin-top:100px;color:green;'>
            ✅ Login Successful
            </h2>

            <div style='text-align:center;'>
            Welcome, {username}
            <br><br>
            <a href='/'>Go To Home</a>
            </div>
            """

        else:

            return """
            <h2 style='text-align:center;margin-top:100px;color:red;'>
            ❌ Invalid Username or Password
            </h2>

            <div style='text-align:center;'>
            <a href='/login'>Try Again</a>
            </div>
            """

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database/movie_recommendation.db')
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users
                (username, email, password)
                VALUES (?, ?, ?)
                """,
                (username, email, password)
            )

            conn.commit()

            return """
            <h2 style='text-align:center;margin-top:100px;'>
            ✅ Registration Successful
            </h2>

            <div style='text-align:center;'>
            <a href='/login'>Go To Login</a>
            </div>
            """

        except sqlite3.IntegrityError:

            return """
            <h2 style='text-align:center;margin-top:100px;color:red;'>
            Username or Email Already Exists
            </h2>

            <div style='text-align:center;'>
            <a href='/register'>Try Again</a>
            </div>
            """

        finally:
            conn.close()

    return render_template('register.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/logout')
def logout():

    session.clear()

    return """
    <h2 style='text-align:center;margin-top:100px;color:green;'>
    ✅ Logout Successful
    </h2>

    <div style='text-align:center;'>
    <a href='/'>Go To Home</a>
    </div>
    """

@app.route('/recommend', methods=['POST'])
def recommend():

    if 'user_id' not in session:
        return  render_template('login_required.html')

    movie = request.form['movie']
    method = request.form['method']

    print("Movie Entered:", movie)
    print("Method Selected:", method)

    if method == "content":
        recommendations = content_recommend(movie)

    elif method == "collaborative":
        recommendations = collaborative_recommend(movie)

    else:
        recommendations = hybrid_recommend(movie)

    print("Recommendations:", recommendations)

    current_time =  datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Save History if user is logged in
    if 'user_id' in session:

        import sqlite3

        conn = sqlite3.connect(
            'database/movie_recommendation.db'
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO history
            (user_id, movie_name, method, recommended_movies , search_date )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session['user_id'],
                movie,
                method,
                ", ".join(recommendations),
                current_time
            )
        )

        conn.commit()
        conn.close()

    return render_template(
        'recommend.html',
        movie=movie,
        method=method,
        recommendations=recommendations
    )


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():

    rating = request.form['rating']
    feedback_text = request.form['feedback_text']

    conn = sqlite3.connect('database/movie_recommendation.db')

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO feedback
        (user_id, feedback_text, rating)
        VALUES (?, ?, ?)
        """,
        (1, feedback_text, rating)
    )

    conn.commit()
    conn.close()

    return """
    <h2 style='text-align:center;margin-top:100px;'>
        ✅ Thank You For Your Feedback!
    </h2>
    <div style='text-align:center;'>
        <a href='/'>Go Back Home</a>
    </div>
 
    """

@app.route('/history')
def history():

    if 'user_id' not in session:
        return redirect('/login')

    import sqlite3

    conn = sqlite3.connect(
        'database/movie_recommendation.db'
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT movie_name,
                method,
                recommended_movies,
                search_date
            FROM history
            WHERE user_id = ?
            ORDER BY id DESC
        """,
        (session['user_id'],)
    )

    history_data = cursor.fetchall()

    conn.close()

    return render_template(
        'history.html',
        history_data=history_data
    )


@app.route('/profile')
def profile():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect(
        'database/movie_recommendation.db'
    )

    cursor = conn.cursor()

    # User Information
    cursor.execute(
        """
        SELECT username, email
        FROM users
        WHERE id = ?
        """,
        (session['user_id'],)
    )

    user = cursor.fetchone()

    # Total Searches
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM history
        WHERE user_id = ?
        """,
        (session['user_id'],)
    )

    total_searches = cursor.fetchone()[0]

    # Total Feedback
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM feedback
        WHERE user_id = ?
        """,
        (session['user_id'],)
    )

    total_feedback = cursor.fetchone()[0]

    # Recent Searches
    cursor.execute(
        """
        SELECT movie_name
        FROM history
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (session['user_id'],)
    )

    recent_movies = cursor.fetchall()

    # Content Searches
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM history
        WHERE user_id = ?
        AND method = 'content'
        """,
        (session['user_id'],)
    )

    content_count = cursor.fetchone()[0]

    # Collaborative Searches
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM history
        WHERE user_id = ?
        AND method = 'collaborative'
        """,
        (session['user_id'],)
    )

    collaborative_count = cursor.fetchone()[0]

    # Hybrid Searches
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM history
        WHERE user_id = ?
        AND method = 'hybrid'
        """,
        (session['user_id'],)
    )

    hybrid_count = cursor.fetchone()[0]

    methods = {
        "Content": content_count,
        "Collaborative": collaborative_count,
        "Hybrid": hybrid_count
    }

    favorite_method = max(
        methods,
        key=methods.get
    )

    conn.close()

    return render_template(
        'profile.html',
        user=user,
        total_searches=total_searches,
        total_feedback=total_feedback,
        recent_movies=recent_movies,
        content_count=content_count,
        collaborative_count=collaborative_count,
        hybrid_count=hybrid_count,
        favorite_method=favorite_method
    )


@app.route('/change_password')
def change_password():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template(
        'change_password.html'
    )

@app.route('/update_password', methods=['POST'])
def update_password():

    if 'user_id' not in session:
        return redirect('/login')

    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:

        return """
        <h2 style='text-align:center;color:red;margin-top:100px;'>
        ❌ New Passwords Do Not Match
        </h2>

        <div style='text-align:center;'>
        <a href='/change_password'>Try Again</a>
        </div>
        """

    conn = sqlite3.connect(
        'database/movie_recommendation.db'
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT password
        FROM users
        WHERE id = ?
        """,
        (session['user_id'],)
    )

    current_password = cursor.fetchone()[0]

    if old_password != current_password:

        conn.close()

        return """
        <h2 style='text-align:center;color:red;margin-top:100px;'>
        ❌ Current Password Is Incorrect
        </h2>

        <div style='text-align:center;'>
        <a href='/change_password'>Try Again</a>
        </div>
        """

    cursor.execute(
        """
        UPDATE users
        SET password = ?
        WHERE id = ?
        """,
        (
            new_password,
            session['user_id']
        )
    )

    conn.commit()
    conn.close()

    return """
    <h2 style='text-align:center;color:green;margin-top:100px;'>
    ✅ Password Updated Successfully
    </h2>

    <div style='text-align:center;'>
    <a href='/profile'>Go To Profile</a>
    </div>
    """

if __name__ == "__main__":
    app.run(debug=True)