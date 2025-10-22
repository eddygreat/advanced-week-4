import urllib.request
import urllib.parse
import http.cookiejar

BASE = 'http://127.0.0.1:5001'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def get(path='/'):
    resp = opener.open(BASE + path)
    data = resp.read().decode('utf-8')
    print(f'GET {path} -> {resp.getcode()} (len={len(data)})')
    return data

def post(path, data):
    data_enc = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(BASE + path, data=data_enc)
    resp = opener.open(req)
    print(f'POST {path} -> {resp.getcode()} Location: {resp.getheader("Location")}')
    return resp

if __name__ == '__main__':
    print('Checking index (unauthenticated)')
    html = get('/')
    assert 'Sorter App' in html

    print('Trying invalid login')
    post('/login', {'username':'alice','password':'wrong'})
    html = get('/')
    assert 'Invalid username or password' in html or 'Sorter App' in html

    print('Logging in with correct credentials')
    post('/login', {'username':'alice','password':'password123'})
    html = get('/')
    if 'Hi, alice' in html:
        print('Login successful, greeting found')
    else:
        print('Login may have failed; page length', len(html))

    print('Logging out')
    post('/logout', {})
    html = get('/')
    print('Done')
