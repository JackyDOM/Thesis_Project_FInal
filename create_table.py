# Author: Clinton Daniel, University of South Florida
# Date: 4/4/2023
# Description: This python script manages the transactions table in database.db
# It keeps only the latest 2 transactions for POL00001

import sqlite3

# Connect to the database
with sqlite3.connect('database.db') as con:
    cur = con.cursor()
    
    # Check if transactions table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
    if not cur.fetchone():
        print("Error: 'transactions' table does not exist. Run the Flask app first to create it.")
    else:
        # Fetch all transactions for POL00001
        cur.execute("SELECT sel, tran_date, time, code, description, loc FROM transactions WHERE policy_id = 'POL00001'")
        transactions = cur.fetchall()
        print("All transactions for POL00001:", transactions)

        # Keep only the latest two transactions (ordered by rowid)
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
        cur.execute("SELECT sel, tran_date, time, code, description, loc FROM transactions WHERE policy_id = 'POL00001'")
        remaining = cur.fetchall()
        print("Remaining transactions:", remaining)