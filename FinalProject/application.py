from flask import Flask, render_template, request, flash, redirect, url_for, session
from reservation import generate_eTicket_number, reserve_seat

import sqlite3
import uuid

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'your_secret_key'  # Set a secret key for session management and flash messages


def get_seating_chart():
    # Initialize seating chart with all seats as "O" (Open)
    seating_chart = [["O" for _ in range(4)] for _ in range(12)]
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("SELECT seatRow, seatColumn FROM reservations")
    reserved_seats = c.fetchall()
    conn.close()
    for seat in reserved_seats:
        row, column = seat
        seating_chart[row - 1][column - 1] = "X"  # Mark seat as reserved
    return seating_chart

def get_cost_matrix():
    # Cost matrix provided by the user
    cost_matrix = [[100, 75, 50, 100] for _ in range(12)]
    return cost_matrix

def get_reserved_seats():
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("SELECT seatRow, seatColumn FROM reservations")
    reserved_seats = c.fetchall()
    conn.close()
    return reserved_seats

def validate_reservation(passenger_name, row, column):
    # Add validation logic here
    return True, ""

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

def calculate_total_sales(seating_chart, cost_matrix):
    total_sales = 0
    for row_idx, row in enumerate(seating_chart):
        for col_idx, seat in enumerate(row):
            if seat == "X":  # If seat is reserved
                total_sales += cost_matrix[row_idx][col_idx]  # Add the corresponding price to total sales
    return total_sales

# Make sure to import the necessary functions from reservation.py
from reservation import generate_eTicket_number, reserve_seat

@app.route('/reservations', methods=['GET', 'POST'])
def reservations():
    # Prepare the seating chart, reserved seats, and cost matrix upfront
    seating_chart = get_seating_chart()  # Fetch the seating chart with seat status
    reserved_seats = get_reserved_seats()  # Fetch the set of reserved seats
    rows = list(range(1, 13))  # Rows 1-12
    columns = list(range(1, 5))  # Columns 1-4
    cost_matrix = get_cost_matrix()  # Retrieve the cost matrix

    # Pair each seat with its cost for easier rendering in the template
    paired_seating_chart = [
        [(seat, cost_matrix[row_idx][col_idx]) for col_idx, seat in enumerate(row)]
        for row_idx, row in enumerate(seating_chart)
    ]

    if request.method == 'POST':
        passenger_name = request.form['passenger_name']
        row = int(request.form['row'])
        column = int(request.form['column'])

        if (row, column) in reserved_seats:
            flash("This seat is already reserved. Please select another seat.", "error")
            return render_template('reservation_form.html', confirmed=False, paired_seating_chart=paired_seating_chart, rows=rows, columns=columns)

        # Call the generate_eTicket_number function from reservation.py
        e_ticket_number = generate_eTicket_number(passenger_name)
        
        try:
            conn = sqlite3.connect('reservations.db')
            c = conn.cursor()
            c.execute("INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber) VALUES (?, ?, ?, ?)", (passenger_name, row, column, e_ticket_number))
            conn.commit()
        except sqlite3.Error as e:
            flash(f'Your reservation could not be processed: {e}. Please try again later.', 'error')
            return render_template('reservation_form.html', confirmed=False, paired_seating_chart=paired_seating_chart, rows=rows, columns=columns)
        finally:
            conn.close()

        flash('Reservation successful!', 'success')
        return render_template('reservation_form.html', confirmed=True, passenger_name=passenger_name, row=row, column=column, e_ticket_number=e_ticket_number, paired_seating_chart=paired_seating_chart, rows=rows, columns=columns)

    # Return the initial form view
    return render_template('reservation_form.html', confirmed=False, paired_seating_chart=paired_seating_chart, rows=rows, columns=columns)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
