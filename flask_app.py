from flask import Flask, render_template, send_file, request
import requests
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
from base64 import b64encode
import smtplib
from email.message import EmailMessage
import tweepy
from nltk.corpus import gutenberg
from nltk import pos_tag
from nltk.corpus import brown
import numpy as np
from nltk.tokenize.treebank import TreebankWordDetokenizer
import re

from matplotlib import rcParams
from pip._internal.vcs import git

matplotlib.use('Agg')
#rcParams.update({'figure.autolayout': True})

"""TEST!!!!!"""

def get_revision_timestamps(TITLE):
    # base URL for API call
    BASE_URL = "http://en.wikipedia.org/w/api.php"

    # empty list to hold our timestamps once retrieved.
    revision_list = []

    # first API call. This loop persists while revision_list is empty
    while not revision_list:
        # set parameters for API call
        parameters = {'action': 'query',
                      'format': 'json',
                      'continue': '',
                      'titles': TITLE,
                      'prop': 'revisions',
                      'rvprop': 'ids|userid|timestamp',
                      'rvlimit': '500'}
        # make the call
        wp_call = requests.get(BASE_URL, params=parameters)
        # get the response
        response = wp_call.json()

        # now we parse the response.
        query = response['query']
        pages = query['pages']
        page_id_list = list(pages.keys())
        page_id = page_id_list[0]
        page_info = pages[str(page_id)]
        revisions = page_info['revisions']

        # Now that the response has been parsed and we can access the revision timestamps, add them to our revision_list.
        for entry in revisions:
            revision_list.append(entry['timestamp'])
        # revision_list is no longer empty, so this loop breaks.


    ## next series of passes, until you're done.
    ## this makes calls until the limit of 500 results per call is no longer reached.
    else:
        while str(len(revisions)) == parameters['rvlimit']:
            start_id = revision_list[-1]
            parameters = {'action': 'query',
                          'format': 'json',
                          'continue': '',
                          'titles': TITLE,
                          'prop': 'revisions',
                          'rvprop': 'ids|userid|timestamp',
                          'rvlimit': '500',
                          'rvstart': start_id}

            # same as before
            wp_call = requests.get(BASE_URL, params=parameters)
            response = wp_call.json()

            query = response['query']
            pages = query['pages']
            page_id_list = list(pages.keys())
            page_id = page_id_list[0]
            page_info = pages[str(page_id)]
            revisions = page_info['revisions']

            for entry in revisions:
                revision_list.append(entry['timestamp'])

    # end by returning a list of revision timestamps
    return revision_list


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('https://github.com/tal-z/PersonalWebsite')
        origin = repo.remotes.origin
        origin.pull()
        return ('Updated PythonAnywhere successfully', 200)
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

    gmail_user = 'talzakendev@gmail.com'
    gmail_password = 'Ethiopiaharrar1!'

    msg = EmailMessage()

    sent_from = 'you@gmail.com'
    to = ['talzaken@gmail.com']
    subject = 'Message From Talzaken.com'
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
        consumer_key = 'aW8uG41Ufh7AbmwwLt1NepeRk'
        consumer_secret = 'eYOQj0W2b0iKJXjCWUwI7CxcNnzFDf5NaMHrSZHBZ6ChfdfQjU'
        access_token = '1309924410363703296-CsYCLirzx4gYfJtc6QMo85I1JfA2m3'
        access_token_secret = 'dYwyxOHmmaZW8XUYPP4SB5mXlw9jznpAr9aw1OT2VIPj2'

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

@app.route('/PlotWikiRevisions')
def PlotWikiRevisions():
    return render_template('PlotWikiRevisions.html')


@app.route('/plot')
def plot():
    page_title = request.args.get('page_title')
    page_title = page_title[0].upper() + page_title[1:]
    print(page_title)
    try:
        timestamps = get_revision_timestamps(page_title)
        timestamps.reverse()

        dates = []
        for stamp in timestamps:
            d = datetime.strptime(stamp, '%Y-%m-%dT%H:%M:%SZ')
            dates.append(d)

        plt.style.use('bmh')
        plt.clf()
        plt.plot()
        plt.plot_date(dates, range(len(dates)), color="green")
        plt.title(f'Revisions to the "{page_title.title()}" Wikipedia Page', wrap=True)
        plt.xlabel('Time')
        plt.ylabel('Revisions count')
        plt.xticks(rotation=60)
        plt.gcf().subplots_adjust(bottom=.2)



        stream = BytesIO()
        plt.savefig(stream, format='png')
        stream.seek(0)

        pngImageB64String = "data:image/png;base64,"
        pngImageB64String += b64encode(stream.getvalue()).decode('utf8')

        return render_template('PlotWikiRevisions.html', image=pngImageB64String)

    except:
        return render_template('PlotWikiRevisions.html', image='https://upload.wikimedia.org/wikipedia/commons/a/a0/Font_Awesome_5_regular_frown.svg')


if __name__ == "__main__":
    app.run()