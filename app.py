from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # used for session management

# Function to get a new database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="samiksha@123",
        database="passport_db"
    )
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, password))
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username or email already exists.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['username'] = user[1]
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')


@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        full_name = request.form['full_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        address = request.form['address']
        id_proof_number = request.form['id_proof_number']
        email = request.form['email']
        application = request.form['application']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO applications (full_name, date_of_birth, gender, address, id_proof_number, email, application)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (full_name, date_of_birth, gender, address, id_proof_number, email, application)
        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return render_template('apply.html', success=True)

    return render_template('apply.html', success=False)



@app.route('/status', methods=['GET', 'POST'])
def check_status():
    status_data = []

    if request.method == 'POST':
        application_id = request.form['application_id']
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert into status_checks
        cursor.execute("""
            INSERT INTO status_checks (application_id, email, status)
            VALUES (%s, %s, %s)
        """, (application_id, email, "Received"))
        conn.commit()

        # Retrieve all status checks
        cursor.execute("SELECT id, application_id, email, status FROM status_checks")
        status_data = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template('status.html', status_data=status_data)
# --- Route to update a status entry ---
@app.route('/update_status/<int:id>', methods=['GET', 'POST'])
def update_status(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_status = request.form['status']

        cursor.execute("""
            UPDATE status_checks
            SET status = %s
            WHERE id = %s
        """, (new_status, id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect('/status')

    # For GET request, fetch the existing record
    cursor.execute("SELECT id, application_id, email, status FROM status_checks WHERE id = %s", (id,))
    record = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('update_status.html', record=record)


# --- Route to delete a status entry ---
@app.route('/delete_status/<int:id>')
def delete_status(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM status_checks WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()
    return redirect('/status')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO contact_messages (name, email, message)
        VALUES (%s, %s, %s)
        """
        values = (name, email, message)

        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('contact.html', success=True)

    return render_template('contact.html', success=False)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
