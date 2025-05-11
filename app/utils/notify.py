from sqlalchemy.orm import Session
from sqlalchemy import text

def add_notification(db: Session, user_id: int, ntype: str, message: str):
    db.execute(text("""INSERT INTO notifications (user_id,type,message) VALUES (:u,:t,:m)"""),{"u":user_id,"t":ntype,"m":message})
    db.commit() 