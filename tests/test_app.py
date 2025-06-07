# tests/test_app.py
import pytest
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_page(client):
    """Test apakah halaman login dapat diakses."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login Sistem Data Karyawan" in response.data

def test_unauthenticated_access(client):
    """Test apakah halaman utama mengarahkan ke login jika belum diautentikasi."""
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Harap login terlebih dahulu." in response.data

def test_successful_login_and_logout(client):
    """Test proses login dan logout yang berhasil."""
    # Login
    response = client.post('/login', data={'username': 'admin', 'password': 'password123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard Data Karyawan" in response.data
    assert b"Login berhasil!" in response.data
    
    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Anda telah logout." in response.data
