from flask import Flask, render_template, send_file, request


app = Flask(__name__)

@app.route("/")
def intro():
    return render_template ("intro.html")

@app.route('/formresponse', methods=["POST"])
def formresponse():
    first_name = request.form.get('fname')
    last_name = request.form.get('lname')
    email = request.form.get('email')
    message = request.form.get('message')
    return render_template ("formresponse.html", first_name=first_name, last_name=last_name, email=email, message=message)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/resume")
def resume():
    return send_file('static/pdf/resume.pdf', attachment_filename='resume.pdf')

@app.route("/composting")
def composting():
    return render_template("composting.html")

@app.route("/coffee")
def coffee():
    return render_template("coffee.html")

@app.route("/hikes")
def hikes():
    return render_template("hikes.html")

@app.route("/hikes/CatalinaIsland")
def CatalinaIsland():
    return render_template("CatalinaIsland.html")

if __name__ == "__main__":
    app.run(debug=True)