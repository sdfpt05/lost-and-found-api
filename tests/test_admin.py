import json
from flask_login import login_user

def test_admin_dashboard_access(test_client, init_database):
    # Login as admin
    response = test_client.post('/auth/login', data=dict(
        username='admin',
        password='adminpassword'
    ), follow_redirects=True)
    assert response.status_code == 200

    # Access admin dashboard
    response = test_client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data

def test_add_item(test_client, init_database):
    # Login as admin
    response = test_client.post('/auth/login', data=dict(
        username='admin',
        password='adminpassword'
    ), follow_redirects=True)
    assert response.status_code == 200

    # Add item
    response = test_client.post('/admin/items', data=dict(
        name='Test Item',
        description='Test Description',
        image_url='http://example.com/image.jpg'
    ), follow_redirects=True)
    assert response.status_code == 201
    assert b'Item added successfully' in response.data

def test_update_item(test_client, init_database):
    # Login as admin
    response = test_client.post('/auth/login', data=dict(
        username='admin',
        password='adminpassword'
    ), follow_redirects=True)
    assert response.status_code == 200

    # Add item
    response = test_client.post('/admin/items', data=dict(
        name='Test Item',
        description='Test Description',
        image_url='http://example.com/image.jpg'
    ), follow_redirects=True)
    assert response.status_code == 201

    # Update item
    response = test_client.put('/admin/items/1', data=dict(
        name='Updated Test Item',
        description='Updated Test Description',
        image_url='http://example.com/updated_image.jpg'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Item updated successfully' in response.data

def test_delete_item(test_client, init_database):
    # Login as admin
    response = test_client.post('/auth/login', data=dict(
        username='admin',
        password='adminpassword'
    ), follow_redirects=True)
    assert response.status_code == 200

    # Add item
    response = test_client.post('/admin/items', data=dict(
        name='Test Item',
        description='Test Description',
        image_url='http://example.com/image.jpg'
    ), follow_redirects=True)
    assert response.status_code == 201

    # Delete item
    response = test_client.delete('/admin/items/1', follow_redirects=True)
    assert response.status_code == 200
    assert b'Item deleted successfully' in response.data
