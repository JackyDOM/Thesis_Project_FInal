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

            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("""
                    INSERT INTO students 
                    (first_name, second_name, age, gender, email, school_name, addr, city, zip) 
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (first_name, second_name, age, gender, email, school_name, addr, city, zip_code))
                policy_id = cur.lastrowid
                policy_id_str = f"POL{policy_id:05d}"

                # Get the actual submission date
                submission_date = datetime.now().strftime("%d/%m/%Y")  # e.g., "06/03/2025"

                # Generate random sel (5-digit number) and code (e.g., B followed by 3 digits)
                def generate_random_sel():
                    return f"{random.randint(10000, 99999):05d}"  # Random 5-digit number

                def generate_random_code():
                    return f"B{random.randint(100, 999)}"

                # Prepare dynamic transactions and insert into database
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
                        "description": f"School Assignment - {school_name}",
                        "loc": "P"
                    }
                ]
                for tran in transactions:
                    cur.execute("""
                        INSERT INTO transactions (policy_id, sel, tran_date, eff_date, code, description, loc)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (policy_id_str, tran["sel"], tran["tran_date"], tran["eff_date"], tran["code"], tran["description"], tran["loc"]))
                con.commit()

            # Create/Open the Excel file and append data
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

            # Prepare data for the template
            data = {
                "policy_id": policy_id_str,
                "first_name": first_name,
                "second_name": second_name,
                "contract_status": "In Force",
                "premium_status": "Prm Paying",
                "register": "IN",
                "transactions": transactions
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
            if not transactions:  # Optional: Handle case where no transactions exist
                transactions = []

        # Prepare data for the template
        data = {
            "policy_id": policy_id,
            "first_name": student["first_name"],
            "second_name": student["second_name"],
            "contract_status": "In Force",
            "premium_status": "Prm Paying",
            "register": "IN",
            "transactions": transactions
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
        except Exception as e:
            con.rollback()
            msg = f"Error in the Edit: {str(e)}"
        finally:
            con.close()
            return render_template('result.html', msg=msg)

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