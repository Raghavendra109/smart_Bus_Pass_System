from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

def get_db():
    return sqlite3.connect("buspass.db")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()
            return "Registration successful!"
        except sqlite3.IntegrityError:
            return "Email already registered!"
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        user = conn.execute(
            "SELECT id, password FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect('/apply')

        return "Invalid email or password!"

    return render_template('login.html')

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        source = request.form['source']
        destination = request.form['destination']
        pass_type = request.form['pass_type']

        prices = {
            'Daily': 70,
            'Monthly': 1200,
            'Quarterly': 3000
        }

        if pass_type not in prices:
            return "Invalid pass type!", 400

        price = prices[pass_type]

        conn = get_db()

        cursor = conn.execute(
             """INSERT INTO bus_passes
            (user_id, source, destination, pass_type, price)
            VALUES (?, ?, ?, ?, ?)""",
            (session['user_id'], source, destination, pass_type, price)
)

        pass_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return redirect(f'/payment/{pass_id}')
    return render_template('apply.html')
@app.route('/payment/<int:pass_id>', methods=['GET', 'POST'])
def payment(pass_id):

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()

    bus_pass = conn.execute(
        """SELECT source, destination, pass_type, price
        FROM bus_passes
        WHERE id = ? AND user_id = ?""",
        (pass_id, session['user_id'])
    ).fetchone()

    if not bus_pass:
        conn.close()
        return "Bus pass not found!", 404

    if request.method == 'POST':

        payment_method = request.form.get('payment_method')

        if payment_method not in ['UPI', 'Card', 'Net Banking']:
            conn.close()
            return "Invalid payment method!", 400

        conn.execute(
            """UPDATE bus_passes
            SET payment_status = 'Paid',
                payment_method = ?,
                payment_date = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?""",
            (payment_method, pass_id, session['user_id'])
        )

        conn.commit()
        conn.close()

        return redirect('/my_passes')

    conn.close()

    return render_template('payment.html', bus_pass=bus_pass)


@app.route('/digital_pass/<int:pass_id>')
def digital_pass(pass_id):

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()

    bus_pass = conn.execute(
        """SELECT bus_passes.id, users.name,
        bus_passes.source, bus_passes.destination,
        bus_passes.pass_type, bus_passes.price,
        bus_passes.payment_status, bus_passes.payment_date
        FROM bus_passes
        JOIN users ON bus_passes.user_id = users.id
        WHERE bus_passes.id = ? AND bus_passes.user_id = ?""",
        (pass_id, session['user_id'])
    ).fetchone()

    conn.close()

    if not bus_pass:
        return "Bus pass not found!", 404

    if bus_pass[6] != 'Paid':
        return "Payment not completed!", 403

    return render_template('digital_pass.html', bus_pass=bus_pass)



@app.route('/verify_pass/<int:pass_id>')
def verify_pass(pass_id):

    conn = get_db()

    bus_pass = conn.execute(
        """SELECT id, source, destination, pass_type,
        payment_status, status
        FROM bus_passes
        WHERE id = ?""",
        (pass_id,)
    ).fetchone()

    conn.close()

    if not bus_pass:
        return "Invalid Bus Pass!", 404

    if bus_pass[4] != 'Paid' or bus_pass[5] != 'Approved':
        return "Bus Pass is not valid or not approved!", 403

    return render_template('verify_pass.html', bus_pass=bus_pass)


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        admin_email = os.environ.get("ADMIN_EMAIL")
        admin_password = os.environ.get("ADMIN_PASSWORD")

        if email == admin_email and password == admin_password:
            session['admin'] = True
            return redirect('/admin')
        else:
            return "Invalid admin credentials"

    return render_template('admin_login.html')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/admin-login')

    conn = get_db()
    passes = conn.execute("""
        SELECT id, user_id, source, destination,
               pass_type, price, status
        FROM bus_passes
    """).fetchall()
    conn.close()

    return render_template('admin.html', passes=passes)


@app.route('/update_status/<int:pass_id>/<status>', methods=['POST'])
def update_status(pass_id, status):
    if not session.get('admin'):
        return redirect('/admin-login')

    if status not in ['Approved', 'Rejected']:
        return "Invalid status!", 400

    conn = get_db()
    conn.execute(
        "UPDATE bus_passes SET status = ? WHERE id = ?",
        (status, pass_id)
    )
    conn.commit()
    conn.close()

    return redirect('/admin')


@app.route('/my_passes')
def my_passes():

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()

    passes = conn.execute(
        """SELECT id, source, destination, pass_type, price, status,
        payment_status, payment_method, payment_date
        FROM bus_passes WHERE user_id = ?""",
        (session['user_id'],)
    ).fetchall()

    conn.close()

    return render_template('my_passes.html', passes=passes)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin-login')


if __name__ == '__main__':
    app.run(debug=True)
