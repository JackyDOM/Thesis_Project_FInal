# Author: Clinton Daniel, University of South Florida
# Date: 4/4/2023
# Description: This python script assumes that you already have
# a database.db file at the root of your workspace.
# This python script will CREATE a table called students 
# in the database.db using SQLite3 which will be used
# to store the data collected by the forms in this app
# Execute this python script before testing or editing this app code. 
# Open a python terminal and execute this script:
# python create_table.py

import sqlite3

# Connect to the database
with sqlite3.connect('database.db') as con:
    cur = con.cursor()
    
    # Fetch all transactions for POL00001
    cur.execute("SELECT sel, tran_date, eff_date, code, description, loc FROM transactions WHERE policy_id = 'POL00001'")
    transactions = cur.fetchall()
    print("All transactions for POL00001:", transactions)

    # Keep only the latest two transactions (assuming ordered by insertion)
    if len(transactions) > 2:
        cur.execute("""
            DELETE FROM transactions 
            WHERE policy_id = 'POL00001' 
            AND sel NOT IN (
                SELECT sel FROM transactions 
                WHERE policy_id = 'POL00001' 
                ORDER BY rowid DESC 
                LIMIT 2
            )
        """)
        con.commit()
        print("Cleaned up old transactions, kept only the latest 2.")
    else:
        print("No cleanup needed, only 2 or fewer transactions exist.")

    # Verify remaining transactions
    cur.execute("SELECT sel, tran_date, eff_date, code, description, loc FROM transactions WHERE policy_id = 'POL00001'")
    remaining = cur.fetchall()
    print("Remaining transactions:", remaining)

