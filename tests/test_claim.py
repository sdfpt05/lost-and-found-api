import json

def test_claim_item(test_client, init_database):
    # Login as user
    response = test_client.post('/auth/login', data=dict(
        username='testuser1',
        password='password123'
    ), follow_redirects=True)
    assert response.status_code == 200

    # Claim item
    response = test_client.post('/claim/1', data=dict(
        date_claimed='2024-07-04',
        description='Claim description'
    ), follow_redirects=True)
    assert response.status_code == 201
    assert b'Claim submitted successfully' in response.data
