from flask import Flask, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import random
import json
import joblib
import csv
import datetime
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'dev-secret-key'

login_manager = LoginManager()
login_manager.init_app(app)

# Load hashed user store from users.json
with open('users.json', 'r', encoding='utf-8') as f:
    USERS = json.load(f)

class User(UserMixin):
        def __init__(self, id):
                self.id = id

@login_manager.user_loader
def load_user(user_id):
        if user_id in USERS:
                return User(user_id)
        return None

NATIONALITIES = ['USA','UK','Canada','Nigeria','Kenya','India','China']
RACES = ['Asian','Black','White','Hispanic','Other']
SEXES = ['M','F']
GRADE_BUCKETS = ['A','B','C','D','F']

def generate_people(n=25):
        people = []
        for i in range(n):
                people.append({
                        'name': f'Person {i+1}',
                        'age': random.randint(10,80),
                        'grade': random.choice(GRADE_BUCKETS),
                        'sex': random.choice(SEXES),
                        'nationality': random.choice(NATIONALITIES),
                        'race': random.choice(RACES)
                })
        return people


# Lazy-loaded model bundle (dict with 'pipeline' and 'label_map')
_MODEL_BUNDLE = None
def load_model_bundle():
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is None:
        try:
            _MODEL_BUNDLE = joblib.load('model.pkl')
        except Exception:
            _MODEL_BUNDLE = None
    return _MODEL_BUNDLE


def log_prediction(user, pred, features):
    # append a CSV row with timestamp, user, prediction, and JSON-encoded features
    row = [datetime.datetime.utcnow().isoformat() + 'Z', user or '', str(pred), json.dumps(features, ensure_ascii=False)]
    try:
        with open('prediction_logs.csv', 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    except Exception:
        # best-effort logging; don't fail prediction for IO errors
        pass

BASE_HTML = """
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Sorter App (single-file)</title>
        <style>
            body{font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; background:#f7fafc; color:#1a202c}
            .container{max-width:1100px;margin:40px auto;background:#fff;padding:24px;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,0.08);} 
            header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
            nav a{margin-left:12px;text-decoration:none;color:#2b6cb0}
            .btn{background:#2b6cb0;color:white;padding:8px 12px;border-radius:6px;border:none;cursor:pointer}
            .btn.secondary{background:#edf2ff;color:#2b6cb0}
            .table{width:100%;border-collapse:collapse}
            .table th,.table td{padding:8px;border-bottom:1px solid #e2e8f0;text-align:left}
            .filter-row{display:flex;gap:8px;margin-bottom:12px;align-items:center}
            .filter-row select{padding:6px;border-radius:6px;border:1px solid #cbd5e1}
            .notice{background:#fff3cd;border:1px solid #ffeeba;padding:10px;border-radius:6px;color:#856404;margin-bottom:12px}
            form.inline{display:inline}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Sorter App</h1>
                <nav>
                    __AUTH_HTML__
                </nav>
            </header>

            __MESSAGE_HTML__

            __CONTENT_HTML__

        </div>
    </body>
</html>
"""

INDEX_CONTENT = """
<section>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div class="filter-row">
            <label>Sort by:
                <select id="sortField">
                    <option value="age">age</option>
                    <option value="grade">grade</option>
                    <option value="sex">sex</option>
                    <option value="nationality">nationality</option>
                    <option value="race">race</option>
                </select>
            </label>
            <label>Order:
                <select id="order"><option value="asc">Ascending</option><option value="desc">Descending</option></select>
            </label>
            <button id="apply" class="btn">Apply</button>
        </div>
        <div>
            <button id="refresh" class="btn secondary">Refresh data</button>
        </div>
    </div>

    <table class="table" id="dataTable">
        <thead>
            <tr><th>Name</th><th>Age</th><th>Grade</th><th>Sex</th><th>Nationality</th><th>Race</th></tr>
        </thead>
        <tbody>
        </tbody>
    </table>
</section>

<script>
const data = {people_json};
const tableBody = document.querySelector('#dataTable tbody');
function render(arr){
    tableBody.innerHTML = '';
    for(const p of arr){
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${p.name}</td><td>${p.age}</td><td>${p.grade}</td><td>${p.sex}</td><td>${p.nationality}</td><td>${p.race}</td>`;
        tableBody.appendChild(tr);
    }
}
render(data);
document.getElementById('apply').addEventListener('click', ()=>{
    const field = document.getElementById('sortField').value;
    const order = document.getElementById('order').value;
    const sorted = [...data].sort((a,b)=>{
        const av = a[field]; const bv = b[field];
        if(av == null) return 1; if(bv == null) return -1;
        if(typeof av === 'string'){
            return order==='asc' ? av.localeCompare(bv) : bv.localeCompare(av);
        }
        return order==='asc' ? (av - bv) : (bv - av);
    });
    render(sorted);
});
document.getElementById('refresh').addEventListener('click', ()=>render(data));
</script>
"""

LOGIN_FORM = """
<form method="POST" action="/login" class="inline">
    <label>Username <input name="username" required></label>
    <label>Password <input name="password" type="password" required></label>
    <button class="btn" type="submit">Login</button>
</form>
"""

REGISTER_FORM = """
<form method="POST" action="/register" style="max-width:420px;display:flex;flex-direction:column;gap:8px">
    <label>Username <input name="username" required style="padding:8px;border-radius:6px;border:1px solid #cbd5e1"></label>
    <label>Password <input name="password" type="password" required style="padding:8px;border-radius:6px;border:1px solid #cbd5e1"></label>
    <div>
        <button class="btn" type="submit">Sign up</button>
        <a href="/" class="btn secondary">Cancel</a>
    </div>
</form>
"""

LOGOUT_FORM = """
<form method="POST" action="/logout" class="inline">
    <button class="btn secondary" type="submit">Logout</button>
</form>
"""

@app.route('/')
def index():
    people = generate_people(25)
    auth_html = ''
    message_html = ''
    if current_user.is_authenticated:
        auth_html = f"<span>Hi, {current_user.id}</span> {LOGOUT_FORM}"
    else:
        auth_html = f"{LOGIN_FORM} <a href=\"/register\" class=\"btn secondary\">Sign up</a>"
    msg = request.args.get('msg')
    if msg:
        message_html = f"<div class=\"notice\">{msg}</div>"
    content_html = INDEX_CONTENT.replace('{people_json}', json.dumps(people))
    html = BASE_HTML.replace('__MESSAGE_HTML__', message_html).replace('__CONTENT_HTML__', content_html)
    html = html.replace('__AUTH_HTML__', auth_html) if '__AUTH_HTML__' in html else html
    return html

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        # show login form as a page
        content_html = LOGIN_FORM
        auth_html = f"<a href=\"/register\" class=\"btn secondary\">Sign up</a>"
        message_html = request.args.get('msg') or ''
        html = BASE_HTML.replace('__AUTH_HTML__', auth_html).replace('__MESSAGE_HTML__', f"<div class=\"notice\">{message_html}</div>" if message_html else '').replace('__CONTENT_HTML__', content_html)
        return html

    # POST: authenticate
    username = request.form.get('username')
    password = request.form.get('password')
    if username in USERS and check_password_hash(USERS[username], password):
        user = User(username)
        login_user(user)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login', msg='Invalid username or password.'))


@app.route('/predict', methods=['POST'])
def predict():
    """Accepts JSON features matching the training features and returns predicted priority label.
    Example JSON body: {"mean radius": 12.3, "mean texture": 15.2, ...}
    """
    bundle = load_model_bundle()
    if bundle is None:
        return ("Model not available", 503)
    pipe = bundle.get('pipeline') if isinstance(bundle, dict) else bundle
    label_map = bundle.get('label_map') if isinstance(bundle, dict) else None
    inv_label_map = {v:k for k,v in label_map.items()} if label_map else None

    try:
        features = request.get_json(force=True)
        # create single-row DataFrame with columns in the same order as training features
        import pandas as _pd
        X = _pd.DataFrame([features])
        pred_enc = pipe.predict(X)[0]
        pred_label = inv_label_map[int(pred_enc)] if inv_label_map is not None else str(pred_enc)
        # log prediction (user may be unauthenticated)
        user = current_user.id if current_user.is_authenticated else ''
        log_prediction(user, pred_label, features)
        return {"prediction": pred_label}
    except Exception as e:
        return ({"error": str(e)}, 400)


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        # show a simple register page
        content_html = REGISTER_FORM
        auth_html = LOGIN_FORM
        message_html = ''
        html = BASE_HTML.replace('__AUTH_HTML__', auth_html).replace('__MESSAGE_HTML__', message_html).replace('__CONTENT_HTML__', content_html)
        return html

    # POST: create user if not exists
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return redirect(url_for('index', msg='Username and password required.'))
    if username in USERS:
        return redirect(url_for('index', msg='Username already exists. Please choose another.'))
    # store hashed password
    USERS[username] = generate_password_hash(password)
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(USERS, f, indent=2)
    # Do not auto-login: redirect user to the login page
    return redirect(url_for('login', msg='Account created. Please log in.'))

@app.route('/logout', methods=['POST'])
@login_required
def logout():
        logout_user()
        return redirect(url_for('index', msg='You have been logged out.'))

if __name__ == '__main__':
        app.run(debug=True)
