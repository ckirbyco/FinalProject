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

    #Verifying user input and logging in as admin
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users:
            if users[username] == password:
                return render_template('admin.html', authenticated=True, username=username)

        error = "Invalid username or password"
        return render_template('admin.html', error=error)
    
    return render_template('admin.html')

@app.route('/reservations')
def reservations():
    return render_template('reservations.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0")
