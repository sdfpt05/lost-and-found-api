from app import create_app, db
from app.models.user import User
from app.models.item import Item
from app.models.claim import Claim
from app.models.lost_report import LostReport
from app.models.found_report import FoundReport
from app.models.reward import Reward
from app.models.comment import Comment
from app.extensions import bcrypt

def populate_database():
    # Create tables
    db.create_all()

    # Create users
    admin = User(username='dinah5', email='dinahngatia86@gmail.com', password=bcrypt.generate_password_hash('adminpassword').decode('utf-8'), is_admin=True)
    user1 = User(username='michaelbjordan', email='michael343@gmail.com', password=bcrypt.generate_password_hash('password123').decode('utf-8'))
    user2 = User(username='jamesk', email='jamesk34@gmail.com', password=bcrypt.generate_password_hash('password123').decode('utf-8'))

    db.session.add(admin)
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    # Create items
    item1 = Item(name='Laptop', description='Silver MacBook Pro', image_url='https://forums.macrumors.com/attachments/99c05799-ed3d-4e10-98a1-db8a0126bc7e-jpeg.1880969/', status='lost')
    item2 = Item(name='Phone', description='Black iPhone', image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSmIaikAVTR8sdoUOUWnp6XUXqPjHAjCedZsQ&s', status='found')
    item3 = Item(name='Backpack', description='Blue backpack', image_url='https://d2jpx6ncc90twu.cloudfront.net/files/product/large/550175.jpg', status='lost')

    db.session.add(item1)
    db.session.add(item2)
    db.session.add(item3)
    db.session.commit()

    # Create claims
    claim1 = Claim(user_id=user1.id, item_id=item1.id, date_claimed='2024-07-04', description='Claiming my lost laptop')
    claim2 = Claim(user_id=user2.id, item_id=item2.id, date_claimed='2024-07-04', description='Claiming the found phone')

    db.session.add(claim1)
    db.session.add(claim2)
    db.session.commit()

    # Create lost reports
    lost_report1 = LostReport(user_id=user1.id, item_id=item1.id, date_reported='2024-07-04', description='Lost my laptop')
    lost_report2 = LostReport(user_id=user1.id, item_id=item3.id, date_reported='2024-07-04', description='Lost my backpack')

    db.session.add(lost_report1)
    db.session.add(lost_report2)
    db.session.commit()

    # Create found reports
    found_report1 = FoundReport(user_id=user2.id, item_id=item2.id, date_reported='2024-07-04', description='Found a phone')

    db.session.add(found_report1)
    db.session.commit()

    # Create rewards
    reward1 = Reward(item_id=item2.id, payer_id=user2.id, receiver_id=user1.id, amount=50, date_paid='2024-07-04')

    db.session.add(reward1)
    db.session.commit()

    comment1 = Comment(user_id=user2.id, item_id=item1.id, content='I think I saw this laptop in the library.')
    db.session.add(comment1)
    db.session.commit()

    print("Database populated successfully.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        populate_database()
