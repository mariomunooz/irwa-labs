import json
import random
from datetime import datetime
import pickle

import requests


# Click Table - Statistics Table 1
class ClickData:
    def __init__(self, click_id, session_id, doc_id, click_counter, query_id, ranking, dwell_time, query_name, browser, operating_system, timestamp):
        self.click_id = click_id
        self.session_id = session_id
        self.doc_id = doc_id
        self.click_counter = click_counter
        self.query_id = query_id
        self.ranking = ranking
        self.dwell_time = dwell_time # amount of time spent on page
        self.query_name = query_name
        self.browser = browser
        self.operating_system = operating_system
        self.timestamp = timestamp


# Request Table - Statistics Table 2
class RequestData:
    def __init__(self, request_id, query_name, query_length, freq_query, url, method, headers, timestamp):
        self.request_id = request_id
        self.query_name = query_name
        self.query_length = query_length
        self.freq_query = freq_query
        self.url = url
        self.method = method
        self.headers = headers
        self.timestamp = timestamp


# Session Table - Statistics Table 3
class SessionData:
    def __init__(self, session_id, num_searches, num_clicks, user_agent, ip_address, timestamp):
        self.session_id = session_id
        self.num_searches = num_searches
        self.num_clicks = num_clicks
        self.user_agent = user_agent
        self.ip_address = ip_address
        #self.country = country
        #self.city = city
        self.timestamp = timestamp


class AnalyticsData:
    """
    An in memory persistence object.
    Declare more variables to hold analytics tables.
    """

    # statistics table 1
    # Click Object Idea: click_id (primary key), session_id, doc_id, query_id, ranking, dwell_time
    # fact_clicks is a dictionary with the click counters: key = doc id | value = click counter
    fact_clicks = dict([])

    # statistics table 2
    # Request Object Idea: request_id (primary key), session_id, url, method, headers, timestamp
    # fact_two is a dictionary with: key = search id | value = search counter
    fact_two = dict([])
    fact_query_name = dict([])

    # statistics table 3
    # Session Object Idea: session_id (primary key), user_agent, ip_address, timestamp
    # fact_two is a dictionary with: key = session id | value = number of queries
    fact_three = dict([])

    # FUNCTIONS WHICH IN THE END WHERE NOT USED!!
    def save_click_data(self, session, doc_id, click_counter, query_id, ranking, dwell_time, search_query, browser, operating_system, timestamp):
        click_id = len(self.fact_clicks) + 1
        session_id = session.get("session_id")
        click_data = ClickData(click_id, session_id, doc_id, click_counter, query_id, ranking, dwell_time,
                               search_query, browser, operating_system, timestamp)

        self.fact_clicks[doc_id] = click_counter
        # self.fact_clicks[doc_id] = click_id
        return click_id

    def save_request_data(self, request, query_length):
        request_id = len(self.fact_two) + 1
        url = request.url
        method = request.method
        headers = list(request.headers)
        timestamp = datetime.now()
        if request_id in self.fact_two:

            request_data = RequestData(request_id, request, query_length, self.fact_two[request_id].freq_query,
                                       url, method, headers, timestamp)
            self.fact_two[request_id] = request_data
            return request_id
        else:
            request_data = RequestData(request_id, query_length, 1,
                                       url, method, headers, timestamp)
            self.fact_two[request_id] = request_data
            return request_id


    def save_session_data(self, request):
        
        session_id = len(self.fact_three) + 1
        user_agent = request.headers.get('User-Agent')
        ip_address = request.remote_addr
        timestamp = datetime.now()

        # Check if session_id exists in self.fact_three
        if session_id in self.fact_three:
            # Assuming self.fact_three[session_id] is an instance of SessionData
            session_data = SessionData(session_id, self.fact_three[session_id].num_searches,
                                       self.fact_three[session_id].num_clicks, user_agent, ip_address, timestamp)
            self.fact_three[session_id] = session_data
            return session_id
        else:
            # Assuming self.fact_three[session_id] is an instance of SessionData
            session_data = SessionData(session_id, 0,0, user_agent, ip_address, timestamp)
            self.fact_three[session_id] = session_data
            return session_id


    def save_query_terms(self, terms: str) -> int:
        print(self)
        return random.randint(0, 100000)

    def save_to_file(self, filename):
        """
        Save the AnalyticsData object to a file using pickle.
        """
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    @classmethod
    def load_from_file(cls, filename):
        """
        Load an AnalyticsData object from a file using pickle.
        """
        with open(filename, 'rb') as file:
            return pickle.load(file)


class ClickedDoc:
    def __init__(self, doc_id, description, counter):
        self.doc_id = doc_id
        self.description = description
        self.counter = counter

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)
