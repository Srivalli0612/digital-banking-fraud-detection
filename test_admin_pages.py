from app import app

# Use Flask test client to check that admin routes render without errors

with app.test_client() as client:
    # Set up a fake admin session
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'admin'
        sess['is_admin'] = True

    endpoints = [
        '/admin/transactions',
        '/admin/fraud-alerts',
        '/admin/users',
        '/admin/model',
        '/admin/reports',
        '/admin/settings',
        '/admin/profile',
        '/api/alerts/count',
        '/api/alerts',
    ]
    for ep in endpoints:
        resp = client.get(ep)
        print(ep, resp.status_code)
        assert resp.status_code == 200, f"{ep} returned {resp.status_code}" 
        if ep.startswith('/api/'):
            data = resp.get_json()
            assert isinstance(data, dict), 'API did not return JSON object'
    # test marking read endpoint
    resp = client.post('/api/alerts/mark_read')
    assert resp.status_code == 200
    resp = client.get('/api/alerts/count')
    assert resp.get_json().get('count') == 0
    print('All admin pages and alert APIs returned expected results')
