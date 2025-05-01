import os
import psycopg2
from datetime import datetime
import sqlite3

# Database connection parameters from app config
db_user = "raj"
db_password = "Rajshah11"
db_name = "liquicity"
db_host = "localhost"
db_port = "5432"

def connect_to_db():
    """Connect to the PostgreSQL database server"""
    conn = None
    try:
        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if conn is not None:
            conn.close()
        return None

def check_transactions_to_user(username="testuser2"):
    """Check transactions sent to a specific user"""
    conn = connect_to_db()
    if conn is None:
        return
    
    try:
        # Create a cursor
        cur = conn.cursor()
        
        # First get the user ID for testuser2
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_result = cur.fetchone()
    
    if not user_result:
            print(f"User {username} not found in the database.")
            return
    
    user_id = user_result[0]
        print(f"Found user {username} with ID {user_id}")
    
        # Query transactions where this user is the recipient
        cur.execute("""
            SELECT 
                t.id, 
                u_sender.username as sender, 
                u_recipient.username as recipient, 
                t.source_amount as amount, 
                t.source_currency, 
                t.target_currency, 
                t.status, 
                t.timestamp, 
                COALESCE(t.payment_source, 'not specified') as payment_source,
                COALESCE(t.transaction_type, 'TRANSFER') as transaction_type
            FROM 
                transactions t
            JOIN 
                users u_sender ON t.sender_id = u_sender.id
            JOIN 
                users u_recipient ON t.recipient_id = u_recipient.id
            WHERE 
                t.recipient_id = %s
            ORDER BY 
                t.timestamp DESC
            LIMIT 10
        """, (user_id,))
        
        transactions = cur.fetchall()
    
    if not transactions:
            print(f"No transactions found where {username} is the recipient.")
        else:
            print(f"\nFound {len(transactions)} transactions where {username} is the recipient:")
            print("-" * 100)
            print(f"{'ID':<5} | {'SENDER':<15} | {'RECIPIENT':<15} | {'AMOUNT':<10} | {'CURRENCY':<8} | {'STATUS':<10} | {'DATE':<20} | {'SOURCE':<15} | {'TYPE':<15}")
            print("-" * 100)
            
            for tx in transactions:
                tx_id, sender, recipient, amount, source_curr, target_curr, status, timestamp, payment_source, tx_type = tx
                print(f"{tx_id:<5} | {sender:<15} | {recipient:<15} | {amount:<10.2f} | {target_curr:<8} | {status:<10} | {timestamp.strftime('%Y-%m-%d %H:%M:%S'):<20} | {payment_source:<15} | {tx_type:<15}")
        
        # Check the wallet balance of testuser2
        cur.execute("""
            SELECT fiat_balance, base_currency
            FROM wallets
            WHERE user_id = %s
        """, (user_id,))
        
        wallet = cur.fetchone()
        if wallet:
            balance, currency = wallet
            print(f"\n{username}'s current wallet balance: {balance:.2f} {currency}")
        else:
            print(f"\n{username} doesn't have a wallet.")
        
        # Close cursor
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def check_transaction_flow(sender="testuser", recipient="testuser2"):
    """Check transactions between two users and their wallet balances"""
    conn = connect_to_db()
    if conn is None:
        return
    
    try:
        # Create a cursor
        cur = conn.cursor()
        
        # Get user IDs
        cur.execute("SELECT id, username FROM users WHERE username IN (%s, %s)", (sender, recipient))
        users = cur.fetchall()
        
        if len(users) < 2:
            print(f"Could not find both users {sender} and {recipient}")
            return
        
        user_dict = {user[1]: user[0] for user in users}
        sender_id = user_dict.get(sender)
        recipient_id = user_dict.get(recipient)
        
        if not sender_id or not recipient_id:
            print(f"Missing user IDs: sender_id={sender_id}, recipient_id={recipient_id}")
            return
        
        # Check wallet balances for both users
        cur.execute("""
            SELECT u.username, w.fiat_balance, w.base_currency
            FROM wallets w
            JOIN users u ON w.user_id = u.id
            WHERE u.id IN (%s, %s)
        """, (sender_id, recipient_id))
        
        wallets = cur.fetchall()
        
        print("\n=== WALLET BALANCES ===")
        for username, balance, currency in wallets:
            print(f"{username}: {balance:.2f} {currency}")
        
        # Get the last 5 transactions between these users
        cur.execute("""
            SELECT 
                t.id, 
                u_sender.username as sender, 
                u_recipient.username as recipient, 
                t.source_amount, 
                t.target_amount,
                t.source_currency, 
                t.target_currency, 
                t.status,
                t.timestamp
            FROM 
                transactions t
            JOIN 
                users u_sender ON t.sender_id = u_sender.id
            JOIN 
                users u_recipient ON t.recipient_id = u_recipient.id
            WHERE 
                (t.sender_id = %s AND t.recipient_id = %s)
                OR 
                (t.sender_id = %s AND t.recipient_id = %s)
            ORDER BY 
                t.timestamp DESC
            LIMIT 5
        """, (sender_id, recipient_id, recipient_id, sender_id))
        
        transactions = cur.fetchall()
        
        if transactions:
            print("\n=== RECENT TRANSACTIONS BETWEEN USERS ===")
            print(f"{'ID':<5} | {'FROM':<15} | {'TO':<15} | {'AMOUNT':<10} | {'TARGET':<10} | {'SOURCE':<5} | {'TARGET':<5} | {'STATUS':<10} | {'TIMESTAMP':<20}")
            print("-" * 100)
            
            for tx in transactions:
                tx_id, tx_sender, tx_recipient, src_amount, tgt_amount, src_curr, tgt_curr, status, timestamp = tx
                print(f"{tx_id:<5} | {tx_sender:<15} | {tx_recipient:<15} | {src_amount:<10.2f} | {tgt_amount:<10.2f} | {src_curr:<5} | {tgt_curr:<5} | {status:<10} | {timestamp.strftime('%Y-%m-%d %H:%M:%S'):<20}")
        else:
            print("\nNo transactions found between these users.")
        
        # Close cursor
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def fix_self_stripe_payments():
    """
    Find and fix Stripe self-payment transactions that incorrectly increased user balance
    """
    print("Starting to check for self-payments via Stripe...")
    
    # Connect to database
    conn = sqlite3.connect('liquicity.db')
    cursor = conn.cursor()
    
    try:
        # Find transactions where:
        # 1. sender_id = recipient_id (self-transfer)
        # 2. payment_source is 'card' or 'bank' (Stripe payment)
        # 3. transaction_type contains 'PAYMENT'
        query = """
        SELECT id, sender_id, recipient_id, stablecoin_amount, source_currency, target_currency, 
               payment_source, transaction_type, timestamp, status
        FROM transactions
        WHERE sender_id = recipient_id 
          AND payment_source IN ('card', 'bank')
          AND transaction_type LIKE '%PAYMENT%'
          AND status = 'completed'
        """
        
        cursor.execute(query)
        self_payments = cursor.fetchall()
        
        if not self_payments:
            print("No self-payments found. Your account is clean.")
            return
        
        print(f"Found {len(self_payments)} self-payment transactions to fix.\n")
        total_to_adjust = 0
        
        # Get the user's wallet for each problematic transaction
        for transaction in self_payments:
            tx_id, user_id = transaction[0], transaction[1]
            amount = transaction[3]  # stablecoin_amount
            source_currency = transaction[4]
            date = transaction[8]
            
            print(f"Transaction #{tx_id}: User {user_id} paid themselves {amount} {source_currency} on {date}")
            total_to_adjust += amount
            
        # Confirm with user
        proceed = input(f"\nTotal adjustment amount: {total_to_adjust}. Fix these transactions? (y/n): ")
        
        if proceed.lower() != 'y':
            print("Operation cancelled.")
            return
        
        # For each transaction, fix the user's wallet balance
        for transaction in self_payments:
            tx_id, user_id, amount = transaction[0], transaction[1], transaction[3]
            
            # Get the current wallet balance
            cursor.execute("SELECT id, fiat_balance FROM wallets WHERE user_id = ?", (user_id,))
            wallet = cursor.fetchone()
            
            if not wallet:
                print(f"Warning: No wallet found for user {user_id}, skipping.")
                continue
                
            wallet_id, current_balance = wallet[0], wallet[1]
            new_balance = current_balance - amount
            
            # Update the wallet balance (subtract the incorrectly added amount)
            cursor.execute(
                "UPDATE wallets SET fiat_balance = ? WHERE id = ?", 
                (new_balance, wallet_id)
            )
            
            # Add a note to the transaction
            cursor.execute(
                "UPDATE transactions SET status = 'adjusted' WHERE id = ?",
                (tx_id,)
            )
            
            print(f"Fixed: Transaction #{tx_id} - Adjusted balance from {current_balance} to {new_balance}")
        
        # Commit all changes
        conn.commit()
        print("\nFix completed! Your wallet balance should now be correct.")
        
except Exception as e:
        conn.rollback()
        print(f"Error during fix: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Check transactions to testuser2
    check_transactions_to_user("testuser2")
    
    # Check transaction flow between users
    print("\n\n" + "="*50)
    print("CHECKING TRANSACTION FLOW BETWEEN USERS")
    print("="*50)
    check_transaction_flow("testuser", "testuser2")
    
    # Fix self-stripe payments
    fix_self_stripe_payments() 