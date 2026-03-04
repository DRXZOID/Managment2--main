from app import app


def test_categories_endpoint():
    client = app.test_client()
    resp = client.get('/api/categories')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'categories' in data
    assert isinstance(data['categories'], list)

