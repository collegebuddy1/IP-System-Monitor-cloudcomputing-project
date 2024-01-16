from flask import Flask, render_template
from firebase_admin import credentials, firestore, initialize_app, db

# Initialise Flask App
app = Flask(__name__)

# Initialise Firestore DB and Fetch the service account key JSON file contents
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
DbName = 'Device_Monitor'
db_collection = db.collection(u'%s' %DbName)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def index():
   
    query = db_collection
    docs = query.stream()

    l = []
    for doc in docs:
        l.append(doc.to_dict())

    for x in range(len(l)):
        if l[x]['status'] == True:
            l[x]['status'] = 'online'
        else:
            l[x]['status'] = 'not detected'
        print('%s %s', l[x]['ip'], l[x]['status'])


    # Render page
    return render_template("index.html", devices=l)






