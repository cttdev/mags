from flask import Flask, render_template
from sassutils.wsgi import SassMiddleware

app = Flask(__name__)

# Make app use sass sytlesheet
app.wsgi_app = SassMiddleware(app.wsgi_app, {
    "mags": ("static/sass", "static/css", "/static/css", False)
})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/hello")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()

    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8080)