import json

def test_user_dashboard_access(test_client, init_database):
    # Login as user
    response = test_client.post('/auth/login', data=dict(
        username='testuser1',
        password='password123'
    ), follow_redirects=True)
    assert response.status_code == 200

    # Access user dashboard
    response = test_client.get('/user/dashboard')
    assert response.status_code == 200
    assert b'User Dashboard' in response.data
