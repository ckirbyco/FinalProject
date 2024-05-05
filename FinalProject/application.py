from flask import Flask, render_template, request

app = Flask(__name__)
app.config["DEBUG"] = True

def read_users_from_file(filename):
    users = {}
    with open(filename, 'r') as file:
        for line in file:
            username, password = line.strip().split(',')
            users[username] = password
    return users

users_file = 'users.txt'
users = read_users_from_file(users_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Connect to the database and check if the user exists
        conn = sqlite3.connect('reservations.db')
        c = conn.cursor()
        c.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['authenticated'] = True
            session['username'] = username
            seating_chart = get_seating_chart()  # Fetch updated seating chart
            cost_matrix = get_cost_matrix()  # Fetch cost matrix
            total_sales = calculate_total_sales(seating_chart, cost_matrix)  # Calculate total sales
            return render_template('admin.html', authenticated=True, username=username, seating_chart=seating_chart, total_sales=total_sales)

        flash("Invalid username or password", "error")

    # If not logged in or login failed, render the login page
    return render_template('admin.html', authenticated=False)

@app.route('/reservations')
def reservations():
    return render_template('reservations.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0")
