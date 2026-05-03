import urllib.request

pages = [
    ('Dashboard', '/'),
    ('Notifications', '/dashboard/notifications/'),
    ('Ecritures', '/finance/ecritures/'),
    ('Projets', '/projects/'),
    ('Fournisseur Form', '/suppliers/fournisseurs/create/'),
    ('Engin Add', '/fleet/engins/add/'),
    ('Profil', '/accounts/profile/'),
]

for name, url in pages:
    try:
        resp = urllib.request.urlopen('http://127.0.0.1:8001' + url)
        code = resp.status
        # 302 = redirect (login required), 200 = OK
        print(f'  {name}: {code} OK')
    except urllib.error.HTTPError as e:
        print(f'  {name}: {e.code} {"REDIRECT" if e.code == 302 else "ERROR"}')
    except Exception as e:
        print(f'  {name}: FAIL ({e})')
