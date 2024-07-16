import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture(scope='module')
def test_client():
    app = create_app()
    app.config.from_object('config.TestingConfig')

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()

@pytest.fixture(scope='module')
def new_user():
    user = User(username='testuser', email='test@gmail.com', password='password123')
    return user

@pytest.fixture(scope='module')
def init_database():
    db.create_all()

    user1 = User(username='testuser1', email='test1@gmail.com', password='password123')
    user2 = User(username='testuser2', email='test2@gmail.com', password='password123')

    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    yield db

    db.session.remove()
    db.drop_all()
