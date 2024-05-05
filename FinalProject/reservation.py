from flask import flash, redirect, render_template, request
import sqlite3
from itertools import zip_longest

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

# Generate eTicket number based on name
def generate_eTicket_number(name):
    sequence = "INFOTC4320"
    result = []
    for char_name, char_seq in zip_longest(name, sequence, fillvalue=''):
        result.append(char_name)
        result.append(char_seq)
    return ''.join(result).rstrip()

# Function to handle reservation requests
def reserve_seat():
    passenger_name = request.form['passenger_name']
    row = request.form['row']
    column = request.form['column']

    # Validate reservation
    is_valid, error_message = validate_reservation(passenger_name, row, column)
    if not is_valid:
        flash(error_message, 'error')
        return redirect('/reservation_form')
    
    # Generate eTicket number
    e_ticket_number = generate_eTicket_number(passenger_name)

    # Insert reservation into database
    try:
        conn = sqlite3.connect('reservations.db')
        c = conn.cursor()
        c.execute("INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber) VALUES (?, ?, ?, ?)", (passenger_name, row, column, e_ticket_number))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        flash(f'Your reservation could not be processed: {e}. Please try again later.', 'error')
        return redirect('/reservation_form')
    
    # Redirect user to confirmation page
    flash(f'Reservation was successful. Your e-ticket number is {e_ticket_number}', 'success')
    return redirect('/confirmation')

# Route for displaying reservation form
def reservation_form():
    return render_template('reservation_form.html')
