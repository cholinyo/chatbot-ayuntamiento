# app.py

from flask import Flask, render_template
from app.routes_api import api

app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/comparativa")
def comparativa():
    return render_template("chat_openai.html")

if __name__ == "__main__":
    app.run(debug=True)
