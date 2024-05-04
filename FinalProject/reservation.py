from flask import Flask, render_template, request, redirect, flash
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = 'Your_hiden_key'

# Validate reservation function
def validate_reservation(passenger_name, row, column):
    if not passenger_name or not row or not column:
        return False, "Fill in all fields."
    try:
        row = int(row)
        column = int(column)
        if row < 1 or row > 12 or column < 1 or column > 4:
            raise ValueError
    except ValueError:
        return False, "Invalid Seat."
    return True, None

# Function to handle reservation requests
@app.route('/reserve' , methods=['POST'])
def reserve_seat():
    passenger_name = request.form['passenger_name' ]
    row = request.form['row']
    column = request.form['column']

# Validate reservation
    is_valid, error_message = validate_reservation(passenger_name, row, column)
    if not is_valid:
        flash(error_message, 'error')
        return redirect('/reservation_form')
    
# Generate e ticket number
    e_ticket_number = str(uuid.uuid4())

# Insert reservation into database
    try:
        conn = sqlite3.connect('reservations.db')
        c = conn.cursor()
        c.execute("INSERT INTO reservations (passengerName , seatRow, seatColumn, eTicketNumber) VALUES (X, X, X, X)", (passenger_name, row, column, e_ticket_number))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        flash('Your reservation could not be processed. Please try again later.' , 'error')
        return redirect('/reservation.form')
    
# Redirect user to confirmation page
    flash('Reservation was successful. Your e-ticket number is ' + e_ticket_number, 'success')
    return redirect('/confirmation')

# Route for displaying reservation form
@app.route('/reservation_form')
def reservation_form():
    return render_template('reservation_form.html')

if __name__ == '__main__':
    app.run(debug=True)