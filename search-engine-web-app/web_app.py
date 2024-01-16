import os
from datetime import datetime
from json import JSONEncoder
import random
from geopy.geocoders import MapQuest

# pip install httpagentparser
import httpagentparser  # for getting the user agent as json
import nltk
from flask import Flask, render_template, session
from flask import request

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc, SessionData, RequestData, ClickData
from myapp.search.load_corpus import load_corpus,document_to_dataframe
from myapp.search.objects import Document, StatsDocument
from myapp.search.search_engine import SearchEngine
from myapp.search.objects import ResultItem, Document
import emoji
import re


import uuid

# Instantiate the Flask application
app = Flask(__name__)

# @app.route("/")
# def hello_world():
#    return "<p>Hello, World!</p>"


# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

#mapquest_api_key = 'YOUR_MAPQUEST_API_KEY'
#geolocator = MapQuest(api_key=mapquest_api_key)
#location = geolocator.geocode("127.0.0.1")

# Random 'secret_key' is used for persisting data in secure cookie
app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
# Open browser dev tool to see the cookies
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'

# Session Unique ID
session_id = 'Session' + str(67983)

click_data = []

# Instantiate our search engine
search_engine = SearchEngine()

# Instantiate our in memory persistence
analytics_data = AnalyticsData()

# print("current dir", os.getcwd() + "\n")
# print("__file__", __file__ + "\n")

# load corpus------------------------------------------
full_path = os.path.realpath(__file__) # get current path
path, filename = os.path.split(full_path)
# print(path + ' --> ' + filename + "\n")
# load documents corpus into memory.
# file_path = path + "/quotes.json"

# file_path = path + "/tweets-data-who.json"
file_path = path + "/merged_data.json"
# print(file_path)
corpus = load_corpus(file_path)
df = document_to_dataframe(corpus)
# print(df)
# print("loaded corpus. first elem:", list(corpus.values())[0])


# Home URL "/"
@app.route('/')
def index():
    print("starting home url /...")

    # flask server creates a session by persisting a cookie in the user's browser.
    # the 'session' object keeps data between multiple requests
    session['some_var'] = "IRWA 2022 home"

    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent)

    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)

    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))

    print(session)

    return render_template('index.html', page_title="Welcome")


@app.route('/search', methods=['POST'])
def search_form_post():
    search_query = request.form['search-query']
    #print("SEARCH QUERY", search_query)

    session['last_search_query'] = search_query

    # I just get randomly an ID - unique identifier
    # search_id = str(uuid.uuid4())

    # DATA COLLECTION FOR SESSIONS TABLE FACT_THREE (num_searches)
    # Update fact_three query counter - Session ID (Global Variable)
    if session_id in analytics_data.fact_three.keys():
        analytics_data.fact_three[session_id] += 1
    else:
        analytics_data.fact_three[session_id] = 1

    # DATA COLLECTION FOR REQUEST TABLE FACT_TWO (search_counter)
    # Get Unique ID
    search_id = analytics_data.save_query_terms(search_query)

    # Query Name: search_query, Query ID: search_id
    # given_query = analytics_data.fact_two.get(search_query)
    if search_id in analytics_data.fact_two.keys():
        analytics_data.fact_two[search_id] += 1
        analytics_data.fact_query_name[search_id] = search_query
    else:
        analytics_data.fact_two[search_id] = 1
        analytics_data.fact_query_name[search_id] = search_query

    # Ranking
    ranked_docs, ranked_values = search_engine.search(search_query, search_id, corpus)

    found_count = len(ranked_docs)
    session['last_found_count'] = found_count
    
    print(session)

    docs = []

    for doc_id in ranked_docs:
        if doc_id in df['Tweet_Id'].values:
            # Assuming 'Tweet_Id' is a unique identifier
            row = df[df['Tweet_Id'] == doc_id].iloc[0]

            # Remove emojis from title and description
            doc_title = re.sub(r'https?://\S+|www\.\S+', '', row["Title"])
            doc_title = re.sub(r'\W', ' ', doc_title)

            doc_description = re.sub(r'https?://\S+|www\.\S+', '', row['Tweet_Text'])
            doc_description = re.sub(r'\W', ' ', doc_description)

            doc = ResultItem(row['Tweet_Id'], doc_title, doc_description, row['Date'], row['Url'],
                             "doc_details?id={}&search_id={}&param2=2".format(row['Tweet_Id'], search_id))
            docs.append(doc)
        else:
            # Handle the case where doc_id is not found in the 'Tweet_Id' column
            print(f"Document with ID {doc_id} not found in the 'Tweet_Id' column.")

    found_count = len(ranked_docs)
    # simulate sort by ranking
    # docs.sort(key=lambda doc: doc.ranking, reverse=True)
    return render_template('results.html', results_list=docs, page_title="Results", found_counter=found_count, request=search_query)


@app.route('/doc_details', methods=['GET'])
def doc_details():
    # getting request parameters:
    # user = request.args.get('user')

    # Capture the time when the user clicks on a result
    click_timestamp = datetime.now()

    print("doc details session: ")
    print(session)

    res = session["some_var"]

    print("recovered var from session:", res)

    # get the query string parameters from request
    clicked_doc_id = request.args["id"]
    query_id = int(request.args["search_id"])  # transform to Integer (p1)
    p2 = int(request.args["param2"])  # transform to Integer

    print("click in id={}".format(clicked_doc_id))

    # UPDATE STATISTICS TABLES/OBJECTS

    # DATA COLLECTION FOR REQUEST TABLE FACT_CLICKS (num_clicks)
    clicked_doc = analytics_data.fact_clicks.get(clicked_doc_id)
    if clicked_doc:
        analytics_data.fact_clicks[clicked_doc_id] += 1
    else:
        analytics_data.fact_clicks[clicked_doc_id] = 1

    # DATA COLLECTION FOR ClickData OBJECT
    # BASIC OBJECT INFO
    # Capture the ranking of a clicked document
    ranked_docs = session.get('ranked_docs', [])
    doc_ranking = ranked_docs.index(clicked_doc_id) + 1 if clicked_doc_id in ranked_docs else None

    # ADDITIONAL INFO
    search_query = session.get('last_search_query')
    user_agent_info = httpagentparser.detect(request.headers.get('User-Agent'))
    browser = user_agent_info.get('browser', {}).get('name', 'Unknown browser')
    operating_system = user_agent_info.get('os', {}).get('name', 'Unknown OS')

    # CLEAN & STORE CLICKED DOC DETAILS
    """
    for element in corpus:
        if element == clicked_doc_id:
            title = corpus[clicked_doc_id].title
            title = re.sub(r'https?://\S+|www\.\S+', '', title)
            title = re.sub(r'\W', ' ', title)
            description = corpus[clicked_doc_id].description
            description = re.sub(r'https?://\S+|www\.\S+', '', description)
            description = re.sub(r'\W', ' ', description)
            date = corpus[clicked_doc_id].doc_date
            likes = corpus[clicked_doc_id].likes
            retweets = corpus[clicked_doc_id].retweets
            url = corpus[clicked_doc_id].url
    """

    title = corpus[clicked_doc_id].title
    title = re.sub(r'https?://\S+|www\.\S+', '', title)
    title = re.sub(r'\W', ' ', title)
    description = corpus[clicked_doc_id].description
    description = re.sub(r'https?://\S+|www\.\S+', '', description)
    description = re.sub(r'\W', ' ', description)
    date = corpus[clicked_doc_id].doc_date
    likes = corpus[clicked_doc_id].likes
    retweets = corpus[clicked_doc_id].retweets
    url = corpus[clicked_doc_id].url


    print("fact_clicks count for id={} is {}".format(clicked_doc_id, analytics_data.fact_clicks[clicked_doc_id]))

    # Calculate dwell time (time spent on the document)
    dwell_time = (datetime.now() - click_timestamp).total_seconds()

    click_id = 'Click' + str(random.randint(0, 100000))
    # Update the previously saved click data with the actual dwell time
    click_data_instance = ClickData(click_id, session_id, clicked_doc_id, analytics_data.fact_clicks[clicked_doc_id], query_id,
                           doc_ranking, dwell_time, analytics_data.fact_two[query_id],
                           browser, operating_system, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # Append click_data to the shared list
    click_data.append(click_data_instance)

    return render_template('doc_details.html', title=title, description=description, date=date, likes=likes, url=url, retweets=retweets)


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """

    docs = []
    # ### Start replace with your code ###

    #Search IDs Counter
    search = []
    for search_id in analytics_data.fact_two:
        freq_query = analytics_data.fact_two[search_id]
        search_query = analytics_data.fact_query_name[search_id]
        query_length = len(search_query.split())
        request_data = RequestData(search_id, search_query, query_length, freq_query,
                                   request.url, request.method, list(request.headers), datetime.now())

        search.append(request_data)

    ###########################################

    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[doc_id]
        count = analytics_data.fact_clicks[doc_id]
        doc = StatsDocument(doc_id, row.title, row.description, row.doc_date, row.url, count)
        docs.append(doc)

    #if location:
        #country = location.raw['components']['country']
        #city = location.raw['components']['city']
    #else:
        #country = "Unknown"
        #city = "Unknown"

    session_num_clicks = sum(analytics_data.fact_clicks.values())
    #session_data = SessionData(session_id, analytics_data.fact_three[session_id], session_num_clicks,
                               #request.headers.get('User-Agent'), request.remote_addr, country, city,
                               #datetime.now())

    session_data = SessionData(session_id, analytics_data.fact_three[session_id], session_num_clicks,
                               request.headers.get('User-Agent'), request.remote_addr,
                               datetime.now())

    # simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)
    return render_template('stats.html', stats_docs=docs, clicks_data=click_data, queries_data=search, session_data=session_data)
    # ### End replace with your code ###


@app.route('/dashboard', methods=['GET'])
def dashboard():
    visited_docs = []
    #print(analytics_data.fact_clicks.keys())

    for doc_id in analytics_data.fact_clicks:
        d: Document = corpus[doc_id]
        doc = ClickedDoc(doc_id, d.description, analytics_data.fact_clicks[doc_id])
        visited_docs.append(doc)

    # simulate sort by ranking
    visited_docs.sort(key=lambda doc: doc.counter, reverse=True)

    visited_ser = []
    for doc in visited_docs:
        visited_ser.append(doc.to_json())

    return render_template('dashboard.html', visited_docs=visited_ser, clicks_data=click_data)


@app.route('/sentiment')
def sentiment_form():
    return render_template('sentiment.html')


@app.route('/sentiment', methods=['POST'])
def sentiment_form_post():
    text = request.form['text']
    nltk.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    score = ((sid.polarity_scores(str(text)))['compound'])
    return render_template('sentiment.html', score=score)


if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
