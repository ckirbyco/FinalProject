from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/reservations')
def reservations():
    return render_template('reservations.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0")