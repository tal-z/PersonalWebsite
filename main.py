from flask import Flask, render_template, send_file


app = Flask(__name__)

@app.route("/")
def hello():
    return render_template ("Intro.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/resume")
def resume():
    return send_file('static/pdf/resume.pdf', attachment_filename='resume.pdf')

@app.route("/composting")
def composting():
    return render_template("composting.html")

@app.route("/CatalinaIsland")
def CatalinaIsland():
    return render_template("CatalinaIsland.html")

@app.route("/coffee")
def coffee():
    return render_template("coffee.html")

if __name__ == "__main__":
    app.run()