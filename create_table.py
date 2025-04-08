from app.database import engine, Base
from app.models import User, Trade, Wallet, Transaction, UserMetadata

Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")