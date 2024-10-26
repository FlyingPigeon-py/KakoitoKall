from n3rz4.base import User, session
from datetime import datetime

async def check_subscription(user_id: int):
    user = session.query(User).filter_by(id=user_id).first()
    if user.subscribe is None:
        return user
    else:
        if datetime.now() >= user.subscribe:

            user.subscribe = None
            session.commit()

    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    return user


    
