# Author: Clinton Daniel, University of South Florida
# Date: 4/4/2023
# Description: This is a Flask App that uses SQLite3 to
# execute (C)reate, (R)ead, (U)pdate, (D)elete operations

from flask import Flask, render_template, request, send_file
import sqlite3
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
import openpyxl  # Add this line to fix the issue
import os
import random
import string
import re

app = Flask(__name__)

# Initialize the database (create table if it doesn’t exist)
def init_db():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                first_name TEXT,
                second_name TEXT,
                age INTEGER,
                gender TEXT,
                email TEXT,
                school_name TEXT,
                addr TEXT,
                city TEXT,
                zip TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                policy_id TEXT,
                sel TEXT,
                tran_date TEXT,
                eff_date TEXT,
                code TEXT,
                description TEXT,
                loc TEXT
            )
        """)
        con.commit()

# Call this once to set up the database
init_db()

# Home Page route
@app.route("/")
def home():
    return render_template("home.html")

# Route to form used to add a new student to the database
@app.route("/enternew")
def enternew():
    return render_template("student.html")

# Route to add a new record (INSERT) student data to the database and export to Excel
# Add this import at the top with other imports
import re

# Modified /addrec route
@app.route("/addrec", methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            # Get data from the form
            first_name = request.form['first_name']
            second_name = request.form['second_name']
            age = request.form['age']
            gender = request.form['gender']
            email = request.form['email']
            school_name = request.form['school_name']
            addr = request.form['add']
            city = request.form['city']
            zip_code = request.form['zip']

            # Define a function to check for special characters
            def has_special_characters(text):
                # Allow only alphanumeric characters, spaces, and basic punctuation
                pattern = r'^[a-zA-Z0-9\s.,-]+$'
                return not bool(re.match(pattern, text))

            # Check fields that shouldn't have special characters
            fields_to_check = {
                'First Name': first_name,
                'Second Name': second_name,
                'School Name': school_name,
                'Address': addr,
                'City': city
            }
            
            # Check for special characters in each field
            for field_name, value in fields_to_check.items():
                if has_special_characters(value):
                    msg = f"No special characters allowed in {field_name}"
                    return render_template('result.html', data={"error": msg})

            # Validate email separately (allowing @ and .)
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return render_template('result.html', data={"error": "Invalid email format"})

            # If we reach here, no special characters were found, proceed with insertion
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("""
                    INSERT INTO students 
                    (first_name, second_name, age, gender, email, school_name, addr, city, zip) 
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (first_name, second_name, age, gender, email, school_name, addr, city, zip_code))
                policy_id = cur.lastrowid
                policy_id_str = f"POL{policy_id:05d}"

                # Rest of your existing code for transactions...
                submission_date = datetime.now().strftime("%d/%m/%Y")
                
                def generate_random_sel():
                    return f"{random.randint(10000, 99999):05d}"

                def generate_random_code():
                    return f"B{random.randint(100, 999)}"

                transactions = [
                    {
                        "sel": generate_random_sel(),
                        "tran_date": submission_date,
                        "eff_date": submission_date,
                        "code": generate_random_code(),
                        "description": f"Student Registration - {first_name} {second_name}",
                        "loc": "P"
                    },
                    {
                        "sel": generate_random_sel(),
                        "tran_date": submission_date,
                        "eff_date": submission_date,
                        "code": generate_random_code(),
                        "description": f"School Name - {school_name}",
                        "loc": "P"
                    }
                ]
                for tran in transactions:
                    cur.execute("""
                        INSERT INTO transactions (policy_id, sel, tran_date, eff_date, code, description, loc)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (policy_id_str, tran["sel"], tran["tran_date"], tran["eff_date"], tran["code"], tran["description"], tran["loc"]))
                con.commit()

            # Rest of your existing code for Excel and rendering...
            file_path = os.path.join(app.static_folder, 'students.xlsx')
            if not os.path.exists(file_path):
                wb = Workbook()
                ws = wb.active
                ws.append(['First Name', 'Second Name', 'Age', 'Gender', 'Email', 'School Name', 'Address', 'City', 'Zip Code'])
            else:
                wb = openpyxl.load_workbook(file_path)
                ws = wb.active
            ws.append([first_name, second_name, age, gender, email, school_name, addr, city, zip_code])
            wb.save(file_path)

            detail_data = [
                {
                    "first_name": first_name,
                    "second_name": second_name,
                    "age": age,
                    "gender": gender,
                    "email": email,
                    "school_name": school_name,
                    "addr": addr,
                    "city": city,
                    "zip": zip_code,
                    "sel": transactions[0]["sel"],
                    "tran_date": transactions[0]["tran_date"],
                    "eff_date": transactions[0]["eff_date"],
                    "code": transactions[0]["code"],
                    "description": transactions[0]["description"],
                    "loc": transactions[0]["loc"],
                    "loc": tran["loc"]
                } 
            ]

             # Add subsequent transactions with only description
            for tran in transactions[1:]:
                detail_data.append({"description": tran["description"]})

            data = {
                "policy_id": policy_id_str,
                "first_name": first_name,
                "second_name": second_name,
                "contract_status": "In Force",
                "premium_status": "Prm Paying",
                "city": city,  # Changed from "register" to "city"
                "transactions": transactions,
                "detail_data": detail_data
            }
            return render_template('result.html', data=data)

        except Exception as e:
            if 'con' in locals():
                con.rollback()
            msg = f"Error in the INSERT: {str(e)}"
            return render_template('result.html', data={"error": msg})
        finally:
            if 'con' in locals():
                con.close()


@app.route("/run", methods=['POST'])
def run():
    try:
        rowid = request.form['id']
        with sqlite3.connect("database.db") as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Fetch student data
            cur.execute("SELECT * FROM students WHERE rowid = ?", (rowid,))
            student = cur.fetchone()
            if not student:
                return render_template('result.html', data={"error": "Student not found"})

            # Fetch transactions
            policy_id = f"POL{int(rowid):05d}"
            cur.execute("SELECT sel, tran_date, eff_date, code, description, loc FROM transactions WHERE policy_id = ?", (policy_id,))
            transactions = [{"sel": row[0], "tran_date": row[1], "eff_date": row[2], "code": row[3], "description": row[4], "loc": row[5]} for row in cur.fetchall()]
            if not transactions:
                transactions = []

            # Prepare detailed data with only the first transaction
            detail_data = [
                {
                    "first_name": student["first_name"],
                    "second_name": student["second_name"],
                    "age": student["age"],
                    "gender": student["gender"],
                    "email": student["email"],
                    "school_name": student["school_name"],
                    "addr": student["addr"],
                    "city": student["city"],
                    "zip": student["zip"],
                    "sel": transactions[0]["sel"],              # First transaction only
                    "tran_date": transactions[0]["tran_date"],
                    "eff_date": transactions[0]["eff_date"],
                    "code": transactions[0]["code"],
                    "description": transactions[0]["description"],  # "Student Registration - Sophea Oudom"
                    "loc": transactions[0]["loc"]
                }
            ] if transactions else []  # Ensure detail_data is empty if no transactions

        # Prepare data for the template
        data = {
            "policy_id": policy_id,
            "first_name": student["first_name"],
            "second_name": student["second_name"],
            "contract_status": "In Force",
            "premium_status": "Prm Paying",
            "city": student["city"],            
            "transactions": transactions,  # Keep all transactions for the transaction table
            "detail_data": detail_data     # Only one entry for the detail table
        }
        return render_template('result.html', data=data)

    except Exception as e:
        return render_template('result.html', data={"error": f"Error in RUN: {str(e)}"})

# Route to SELECT all data from the database and display in a table      
@app.route('/list')
def list():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM students")
    rows = cur.fetchall()
    con.close()
    return render_template("list.html", rows=rows)

# Route that will SELECT a specific row in the database then load an Edit form 
@app.route("/edit", methods=['POST', 'GET'])
def edit():
    if request.method == 'POST':
        try:
            id = request.form['id']
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT rowid, * FROM students WHERE rowid = ?", (id,))
            rows = cur.fetchall()
        except:
            rows = []
        finally:
            con.close()
            return render_template("edit.html", rows=rows)

# Route used to execute the UPDATE statement on a specific record in the database
@app.route("/editrec", methods=['POST', 'GET'])
def editrec():
    if request.method == 'POST':
        try:
            rowid = request.form['rowid']
            first_name = request.form['first_name']
            second_name = request.form['second_name']
            age = request.form['age']
            gender = request.form['gender']
            email = request.form['email']
            school_name = request.form['school_name']
            addr = request.form['add']
            city = request.form['city']
            zip_code = request.form['zip']

            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("""
                    UPDATE students 
                    SET first_name = ?, second_name = ?, age = ?, gender = ?, email = ?, 
                        school_name = ?, addr = ?, city = ?, zip = ?
                    WHERE rowid = ?
                """, (first_name, second_name, age, gender, email, school_name, addr, city, zip_code, rowid))
                con.commit()
                msg = "Record successfully edited in the database"
                data = {"message": msg}  # Pass success message in data dictionary

        except Exception as e:
            con.rollback()
            msg = f"Error in the Edit: {str(e)}"
            data = {"error": msg}  # Pass error message in data dictionary
        finally:
            con.close()
            return render_template('result.html', data=data)  # Return data instead of msg

# Route used to DELETE a specific record in the database    
@app.route("/delete", methods=['POST', 'GET'])
def delete():
    if request.method == 'POST':
        try:
            rowid = request.form['id']
            file_path = os.path.join(app.static_folder, 'students.xlsx')
            policy_id = f"POL{int(rowid):05d}"  # Calculate policy_id for transactions

            # Step 1: Delete the record from the database (students and transactions)
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                # Delete from students table
                cur.execute("DELETE FROM students WHERE rowid=?", (rowid,))
                # Delete associated transactions
                cur.execute("DELETE FROM transactions WHERE policy_id=?", (policy_id,))
                con.commit()

                # Step 2: Fetch all remaining records from the database
                cur.execute("SELECT * FROM students")
                rows = cur.fetchall()

            # Step 3: Rewrite the Excel file with the updated data
            wb = Workbook()
            ws = wb.active
            ws.append(['First Name', 'Second Name', 'Age', 'Gender', 'Email', 'School Name', 'Address', 'City', 'Zip Code'])
            for row in rows:
                ws.append(row)
            wb.save(file_path)

            # Prepare data for the template (success case)
            data = {
                "message": "Record successfully deleted from the database and Excel file"
            }
        except Exception as e:
            if 'con' in locals():
                con.rollback()
            # Prepare data for the template (error case)
            data = {
                "error": f"Error in the DELETE: {str(e)}"
            }
        finally:
            if 'con' in locals():
                con.close()
            return render_template('result.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)