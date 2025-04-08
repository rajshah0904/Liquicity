import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from app.models import Base, User, BankAccount

# Check if the User class has bank_accounts relationship
print("Checking User model relationships...")
user_attrs = dir(User)
print(f"User attributes: {[attr for attr in user_attrs if not attr.startswith('_')]}")

# Check if the BankAccount class has user relationship
print("\nChecking BankAccount model relationships...")
bank_attrs = dir(BankAccount)
print(f"BankAccount attributes: {[attr for attr in bank_attrs if not attr.startswith('_')]}")

# Check the relationship definitions
print("\nUser class relationship mappings:")
if hasattr(User, 'bank_accounts'):
    rel = getattr(User, 'bank_accounts')
    print(f"User.bank_accounts: {rel.prop}")
else:
    print("User does not have bank_accounts relationship")

print("\nBankAccount class relationship mappings:")
if hasattr(BankAccount, 'user'):
    rel = getattr(BankAccount, 'user')
    print(f"BankAccount.user: {rel.prop}")
else:
    print("BankAccount does not have user relationship")

print("\nAdding bank_accounts relationship to User class if missing...")
if not hasattr(User, 'bank_accounts'):
    User.bank_accounts = relationship("BankAccount", back_populates="user")
    print("Added bank_accounts relationship to User class")
else:
    print("User already has bank_accounts relationship")

print("\nFixing BankAccount.user relationship...")
BankAccount.user = relationship("User", back_populates="bank_accounts")
print("Fixed BankAccount.user relationship")

print("\nDone. Please restart the server to apply these changes.") 