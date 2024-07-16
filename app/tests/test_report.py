import json

def test_report_lost_item(test_client, init_database):
    # Login as user
    response = test_client.post('/auth/login', data=dict(
        username='testuser1',
        password='password123'
    ), follow_redirects=True)
    assert response.status_code == 200

    # Report lost item
    response = test_client.post('/report/lost', data=dict(
        item_id=1,
        date_reported='2024-07-04',
        description='Lost description'
    ), follow_redirects=True)
    assert response.status_code == 201
    assert b'Lost report submitted successfully' in response.data

def test_report_found_item(test_client, init_database):
    # Login as user
    response = test_client.post('/auth/login', data=dict(
        username='testuser1',
        password='password123'
    ), follow_redirects=True)
    assert response.status_code == 200

    # Report found item
    response = test_client.post('/report/found', data=dict(
        item_id=1,
        date_reported='2024-07-04',
        description='Found description'
    ), follow_redirects=True)
    assert response.status_code == 201
    assert b'Found report submitted successfully' in response.data
