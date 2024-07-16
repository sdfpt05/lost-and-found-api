import json

def test_offer_reward(test_client, init_database):
    # Login as user
    response = test_client.post('/auth/login', data=dict(
        username='testuser1',
        password='password123'
    ), follow_redirects=True)
    assert response.status_code == 200

    # Offer reward
    response = test_client.post('/reward/1', data=dict(
        receiver_id=2,
        amount=100,
        date_paid='2024-07-04'
    ), follow_redirects=True)
    assert response.status_code == 201
    assert b'Reward offered successfully' in response.data
