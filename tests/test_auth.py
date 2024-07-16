import json

def test_register(test_client):
    response = test_client.post('/auth/register', data=dict(
        username='testuser',
        email='test@gmail.com',
        password='password123'
    ), follow_redirects=True)
    assert response.status_code == 201
    assert b'Registered successfully' in response.data

def test_login(test_client, init_database):
    response = test_client.post('/auth/login', data=dict(
        username='testuser1',
        password='password123'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Login successful' in response.data

def test_logout(test_client, init_database):
    test_client.post('/auth/login', data=dict(
        username='testuser1',
        password='password123'
    ), follow_redirects=True)
    response = test_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged out successfully' in response.data
