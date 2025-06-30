from clean_backend.database import SessionLocal, Base, engine
from clean_backend.models import User, BridgeUser


def seed_bridge_users():
    """Copy existing customer & wallet info from users_v2 into bridge_users_v2."""
    # Ensure table exists
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        users = db.query(User).filter(
            (User.bridge_customer_id != None) | (User.bridge_wallet_id != None)  # noqa: E711
        ).all()
        created = 0
        updated = 0
        for u in users:
            rec = db.query(BridgeUser).filter(BridgeUser.user_id == u.id).first()
            if rec is None:
                db.add(
                    BridgeUser(
                        user_id=u.id,
                        bridge_customer_id=u.bridge_customer_id,
                        bridge_wallet_id=u.bridge_wallet_id,
                    )
                )
                created += 1
            else:
                # update if data changed
                if rec.bridge_customer_id != u.bridge_customer_id or rec.bridge_wallet_id != u.bridge_wallet_id:
                    rec.bridge_customer_id = u.bridge_customer_id
                    rec.bridge_wallet_id = u.bridge_wallet_id
                    updated += 1
        db.commit()
    print(f"Seed complete – created {created}, updated {updated} bridge user records")


if __name__ == "__main__":
    seed_bridge_users() 