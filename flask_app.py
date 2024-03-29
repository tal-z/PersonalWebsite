import os
import hmac
import hashlib

from flask import Flask, render_template, send_file, request
import smtplib
from email.message import EmailMessage
import tweepy
from nltk.corpus import gutenberg
from nltk import pos_tag
from nltk.corpus import brown
import numpy as np
from nltk.tokenize.treebank import TreebankWordDetokenizer
import re
from dotenv import load_dotenv
load_dotenv()
try:
    import git
except:
    from pip._internal.vcs import git



"""  :)  """


def is_valid_signature(x_hub_signature, data, private_key):
    # x_hub_signature and data are from the webhook payload
    # private key is your webhook secret
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        github_secret_token = os.getenv('github_secret_token')
        x_hub_signature = request.headers.get('X-Hub-Signature')
        if is_valid_signature(x_hub_signature, request.data, github_secret_token):
            repo = git.Repo('mysite/PersonalWebsite')
            origin = repo.remotes.origin
            origin.pull()
            return ('Updated PythonAnywhere successfully', 200)
        else:
            return ('Signature not validated', 400)
    else:
        return ('Wrong event type', 400)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route("/")
def intro():
    return render_template ("intro.html")

@app.route('/formresponse', methods=["POST"])
def formresponse():
    first_name = request.form.get('fname')
    last_name = request.form.get('lname')
    email = request.form.get('email')
    message = request.form.get('message')

    gmail_user = os.getenv('gmail_user')
    gmail_password = os.getenv('gmail_password')

    msg = EmailMessage()

    sent_from = 'you@gmail.com'
    to = ['talzaken@gmail.com']
    subject = 'Message From talzaken.pythonanywhere.com'
    body = message

    email_text = f"""
    Sent By:
    First Name:{first_name}
    Last Name: {last_name}
    Email Address: {email}

    Message:
    {body}
    """
    msg.set_content(email_text)
    msg['Subject'] = subject
    msg['From'] = sent_from
    msg['To'] = to

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()

        print('Email sent!')

    except:
        print('Something went wrong...')

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

@app.route("/OtherStuff")
def OtherStuff():
    return render_template("OtherStuff.html")

@app.route("/coffee")
def coffee():
    return render_template("coffee.html")

@app.route("/hikes")
def hikes():
    return render_template("hikes.html")

@app.route("/hikes/CatalinaIsland")
def CatalinaIsland():
    return render_template("CatalinaIsland.html")

@app.route("/NLP")
def NLP():
    return render_template("NLP.html")

@app.route("/writerbot")
def writerbot():
    return render_template("WriterBot.html")

@app.route("/bot_write/", methods=['POST'])
def bot_write():
    """Step 1: Build dictionary of tagged words."""

    tagged_words = brown.tagged_words()
    tagged_words_dict = {}
    for tup in tagged_words:
        if tup[1] in tagged_words_dict:
            tagged_words_dict[tup[1]].append(tup[0].lower())
        else:
            tagged_words_dict[tup[1]] = []
            tagged_words_dict[tup[1]].append(tup[0].lower())

    '''Uncomment the following two lines if we just want to use the brown corpus's vocabulary, and ignore word frequency.'''
    for k, v in tagged_words_dict.items():
        tagged_words_dict[k] = list(set(v))

    def write_sentence(tag_dict=tagged_words_dict):

        """Step 2: Choose a work, identify the author, and choose a sentence."""
        work = gutenberg.fileids()[np.random.randint(len(gutenberg.fileids()))]
        author = re.findall('(\w+)-', work)[0].title()

        sentences = gutenberg.sents(work)
        vocab = set(gutenberg.words(work))

        rndm_sentence = sentences[np.random.randint(len(sentences))]

        tagged_rndm_sentence = pos_tag(rndm_sentence)

        """Step 3: Replace every word in the sentence with another word that can have the same POS."""

        tag_dict = {k: [word for word in v if word in vocab] for k, v in tag_dict.items()}
        tag_dict = {k: v for k, v in tag_dict.items() if v}

        new_sentence = [tup[0] if tup[1] in ['DT', 'NNP', '.', ',', "''", ':'] or tup[1] not in tag_dict
                        else tag_dict[tup[1]][np.random.randint(len(tag_dict[tup[1]]))]
                        for tup in tagged_rndm_sentence]

        new_detokenized_sentence = str(TreebankWordDetokenizer().detokenize(new_sentence))
        new_detokenized_sentence = new_detokenized_sentence[0].upper() + new_detokenized_sentence[1:]
        if new_detokenized_sentence[-1].isalnum():
            new_detokenized_sentence = new_detokenized_sentence + '.'


        if len(new_sentence) <= 3:
            return write_sentence()
        if len(author) + len(new_detokenized_sentence) > 278:
            return write_sentence()
        else:
            return (author, re.sub(r'[\)\\"]', '', new_detokenized_sentence))

    def post_sentence():
        consumer_key = os.getenv('consumer_key')
        consumer_secret = os.getenv('consumer_secret')
        access_token = os.getenv('access_token')
        access_token_secret = os.getenv('access_token_secret')

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        ws = write_sentence()

        api.update_status(f"{ws[0]}: {ws[1]}")
    post_sentence()
    return render_template('WriterBot.html');


@app.route('/wikipedia')
def wikipedia():
    return render_template('wikipedia.html')

@app.route('/mapping')
def mapping():
    return render_template('mapping.html')

@app.route('/mapping/DOEArt')
def DOEArt():
    return render_template('DOEArt.html')


@app.route('/tMinusMbta')
def tMinusMbta():
    return render_template('tMinusMbta.html')



@app.route('/digital_art')
def digital_art():
    return render_template('digitalart.html')


if __name__ == "__main__":
    app.run()