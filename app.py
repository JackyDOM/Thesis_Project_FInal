# Author: Clinton Daniel, University of South Florida
# Date: 4/4/2023
# Description: This is a Flask App that uses SQLite3 to
# execute (C)reate, (R)ead, (U)pdate, (D)elete operations

from flask import Flask, render_template, request, send_file
import sqlite3
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
import openpyxl
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
                city TEXT
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

@app.route("/addrec", methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            # Get data from the form (removed zip)
            first_name = request.form['first_name']
            second_name = request.form['second_name']
            age = request.form['age']
            gender = request.form['gender']
            email = request.form['email']
            school_name = request.form['school_name']
            addr = request.form['add']
            city = request.form['city']

            # Define a function to check for special characters
            def has_special_characters(text):
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
            
            for field_name, value in fields_to_check.items():
                if has_special_characters(value):
                    msg = f"No special characters allowed in {field_name}"
                    return render_template('result.html', data={"error": msg})

            # Validate email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return render_template('result.html', data={"error": "Invalid email format"})

            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("""
                    INSERT INTO students 
                    (first_name, second_name, age, gender, email, school_name, addr, city) 
                    VALUES (?,?,?,?,?,?,?,?)
                """, (first_name, second_name, age, gender, email, school_name, addr, city))
                policy_id = cur.lastrowid
                policy_id_str = f"POL{policy_id:05d}"

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

            file_path = os.path.join(app.static_folder, 'students.xlsx')
            if not os.path.exists(file_path):
                wb = Workbook()
                ws = wb.active
                ws.append(['First Name', 'Second Name', 'Age', 'Gender', 'Email', 'School Name', 'Address', 'City'])
            else:
                wb = openpyxl.load_workbook(file_path)
                ws = wb.active
            ws.append([first_name, second_name, age, gender, email, school_name, addr, city])
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
                    "sel": transactions[0]["sel"],
                    "tran_date": transactions[0]["tran_date"],
                    "eff_date": transactions[0]["eff_date"],
                    "code": transactions[0]["code"],
                    "description": transactions[0]["description"],
                    "loc": transactions[0]["loc"]
                }
            ]

            data = {
                "policy_id": policy_id_str,
                "first_name": first_name,
                "second_name": second_name,
                "city": city,
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
            cur.execute("SELECT * FROM students WHERE rowid = ?", (rowid,))
            student = cur.fetchone()
            if not student:
                return render_template('result.html', data={"error": "Student not found"})

            policy_id = f"POL{int(rowid):05d}"
            cur.execute("SELECT sel, tran_date, eff_date, code, description, loc FROM transactions WHERE policy_id = ?", (policy_id,))
            transactions = [{"sel": row[0], "tran_date": row[1], "eff_date": row[2], "code": row[3], "description": row[4], "loc": row[5]} for row in cur.fetchall()]
            if not transactions:
                transactions = []

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
                    "sel": transactions[0]["sel"],
                    "tran_date": transactions[0]["tran_date"],
                    "eff_date": transactions[0]["eff_date"],
                    "code": transactions[0]["code"],
                    "description": transactions[0]["description"],
                    "loc": transactions[0]["loc"]
                }
            ] if transactions else []

        data = {
            "policy_id": policy_id,
            "first_name": student["first_name"],
            "second_name": student["second_name"],
            "city": student["city"],
            "transactions": transactions,
            "detail_data": detail_data
        }
        return render_template('result.html', data=data)

    except Exception as e:
        return render_template('result.html', data={"error": f"Error in RUN: {str(e)}"})

@app.route('/list')
def list():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM students")
    rows = cur.fetchall()
    con.close()
    return render_template("list.html", rows=rows)

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

            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("""
                    UPDATE students 
                    SET first_name = ?, second_name = ?, age = ?, gender = ?, email = ?, 
                        school_name = ?, addr = ?, city = ?
                    WHERE rowid = ?
                """, (first_name, second_name, age, gender, email, school_name, addr, city, rowid))
                con.commit()
                msg = "Record successfully edited in the database"
                data = {"message": msg}

        except Exception as e:
            con.rollback()
            msg = f"Error in the Edit: {str(e)}"
            data = {"error": msg}
        finally:
            con.close()
            return render_template('result.html', data=data)

@app.route("/delete", methods=['POST', 'GET'])
def delete():
    if request.method == 'POST':
        try:
            rowid = request.form['id']
            file_path = os.path.join(app.static_folder, 'students.xlsx')
            policy_id = f"POL{int(rowid):05d}"

            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("DELETE FROM students WHERE rowid=?", (rowid,))
                cur.execute("DELETE FROM transactions WHERE policy_id=?", (policy_id,))
                con.commit()

                cur.execute("SELECT * FROM students")
                rows = cur.fetchall()

            wb = Workbook()
            ws = wb.active
            ws.append(['First Name', 'Second Name', 'Age', 'Gender', 'Email', 'School Name', 'Address', 'City'])
            for row in rows:
                ws.append(row)
            wb.save(file_path)

            data = {
                "message": "Record successfully deleted from the database and Excel file"
            }
        except Exception as e:
            if 'con' in locals():
                con.rollback()
            data = {
                "error": f"Error in the DELETE: {str(e)}"
            }
        finally:
            if 'con' in locals():
                con.close()
            return render_template('result.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)