#Imports from Colab Files
import nltk
nltk.download("stopwords")

from collections import defaultdict
from array import array
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import math
import numpy as np
import collections
from numpy import linalg as la
import json
import re
import emoji
import time
#import seaborn as sns
#from wordcloud import WordCloud
from collections import Counter
# import matplotlib.pyplot as plt
import pandas as pd

#Algorithms seen in other parts of the Project

# Process Tweets
def build_terms(text):
    """
    Preprocess the article text (title + body) removing stop words, stemming,
    transforming in lowercase and return the tokens of the text.

    Argument:
    line -- string (text) to be preprocessed

    Returns:
    line - a list of tokens corresponding to the input text after the preprocessing
    """
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words("english"))

    url_pattern = r'https?://\S+|www\.\S+'
    urls = re.findall(url_pattern, text)
    # Remove URLs #
    line = re.sub(url_pattern, '', text)
    # Transform into lowercase
    line = line.lower()
    # Remove punctuation marks
    line = re.sub(r'[!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]', '', text)
    # Remove emojis
    line = re.sub(r'\W', ' ', line)
    ## Tokenize the text to get a list of terms
    line = line.split()
    # Eliminate the stopwords (HINT: use List Comprehension)
    line = [word for word in line if word not in stop_words]
    # Perform stemming (HINT: use List Comprehension)
    line = [stemmer.stem(word) for word in line]

    return line, urls

# Inverted Index Function
def create_index(lines):
    """
    Implement the inverted index

    Argument:
    lines -- collection of tweets

    Returns:
    index - the inverted index (implemented through a Python dictionary) containing terms as keys and the corresponding
    list of documents where these keys appears in (and the positions) as values.
    """
    index = defaultdict(list)
    tweet_index = {}  # dictionary to map page titles to page ids

    for line in lines:  # lines contain all tweets
        tweet_id = line[0]
        terms = line[1]
        tweet_index[tweet_id] = line[1]


        current_page_index = {}

        for position, term in enumerate(terms): #Loop over all terms
            try:
                current_page_index[term][1].append(position)
            except:
                current_page_index[term]=[tweet_id, array('I',[position])] #'I' indicates unsigned int (int in Python)

        #merge the current page index with the main index
        for term_page, posting_page in current_page_index.items():
            index[term_page].append(posting_page)

    return index, tweet_index

# Search for text in collection using Inverted Index
def search(query, index):
    """
    The output is the list of documents that contain any of the query terms.
    So, we will get the list of documents for each query term, and take the union of them.
    """
    query = build_terms(query)
    docs = set()
    for term in query:
        for i in range(len(term)):
            try:
                # store in term_docs the ids of the docs that contain "term"
                term_docs = [posting[0] for posting in index[term[i]]]
                #print(f"Query Term: {term[i]}, Matching Docs: {term_docs}")
                # docs = docs Union term_docs
                docs = docs.union(term_docs)

            except:
                #term is not in index
                pass
    docs = list(docs)
    return docs

def create_index_tfidf(lines, num_tweets):
    index = defaultdict(list)
    tweet_index = {}
    tf = defaultdict(list)
    df = defaultdict(int)
    idf = defaultdict(float)

    for line in lines:
        tweet_id, terms = line[0], line[1]
        tweet_index[tweet_id] = terms

        current_page_index = defaultdict(lambda: [tweet_id, array('I')])

        norm = 0
        for position, term in enumerate(terms):
            current_page_index[term][1].append(position)
            norm += 1  # Increment norm in the same loop

        norm = math.sqrt(norm)

        for term, posting in current_page_index.items():
            tf_value = np.round(len(posting[1]) / norm, 4)
            tf[term].append(tf_value)
            df[term] += 1
            index[str(term)].append(posting)

    for term in df:
        idf[term] = np.round(np.log(float(num_tweets / df[term])), 4)

    return index, tf, df, idf, tweet_index


# Ranking based on tf-idf Weights
def rank_documents(terms, docs, index, idf, tf):
    """
    Perform the ranking of the results of a search based on the tf-idf weights

    Argument:
    terms -- list of query terms
    docs -- list of documents, to rank, matching the query
    index -- inverted index data structure
    idf -- inverted document frequencies
    tf -- term frequencies
    title_index -- mapping between page id and page title

    Returns:
    Print the list of ranked documents
    """

    # I'm interested only on the element of the docVector corresponding to the query terms
    # The remaining elements would became 0 when multiplied to the query_vector
    doc_vectors = defaultdict(lambda: [0] * len(terms)) # I call doc_vectors[k] for a nonexistent key k, the key-value pair (k,[0]*len(terms)) will be automatically added to the dictionary
    query_vector = [0] * len(terms)

    # compute the norm for the query tf
    query_terms_count = collections.Counter(terms)  # get the frequency of each term in the query.
    # Example: collections.Counter(["hello","hello","world"]) --> Counter({'hello': 2, 'world': 1})
    # HINT: use when computing tf for query_vector

    query_norm = la.norm(list(query_terms_count.values()))

    for termIndex, term in enumerate(terms):  #termIndex is the index of the term in the query
        if term not in index:
            continue

        ## Compute tf*idf(normalize TF as done with documents)
        query_vector[termIndex]=(query_terms_count[term]/query_norm) * idf[term]

        # Generate doc_vectors for matching docs
        for doc_index, (doc, postings) in enumerate(index[term]):
            # Example of [doc_index, (doc, postings)]
            # 0 (26, array('I', [1, 4, 12, 15, 22, 28, 32, 43, 51, 68, 333, 337]))
            # 1 (33, array('I', [26, 33, 57, 71, 87, 104, 109]))
            # term is in doc 26 in positions 1,4, .....
            # term is in doc 33 in positions 26,33, .....

            #tf[term][0] will contain the tf of the term "term" in the doc 26
            if doc in docs:
                doc_vectors[doc][termIndex] = tf[term][doc_index] * idf[term]  # TODO: check if multiply for idf

    # Calculate the score of each doc
    # compute the cosine similarity between queyVector and each docVector:
    # HINT: you can use the dot product because in case of normalized vectors it corresponds to the cosine similarity
    # see np.dot

    doc_scores=[[np.dot(curDocVec, query_vector), doc] for doc, curDocVec in doc_vectors.items() ]
    doc_scores.sort(reverse=True)
    result_docs = [x[1] for x in doc_scores]
    result_scores = [x[0] for x in doc_scores]
    #print document titles instead if document id's
    #result_docs=[ title_index[x] for x in result_docs ]
    if len(result_docs) == 0:
        print("No results found, try again")
    #print ('\n'.join(result_docs), '\n')
    return result_docs, result_scores


# List of Docs that contain any of the query terms
def search_tf_idf(query, index, tf, df, idf, title_index):
    """
    output is the list of documents that contain any of the query terms.
    So, we will get the list of documents for each query term, and take the union of them.
    """
    query = build_terms(query)
    #print(query)

    #docs = set()
    # Remove empty lists from the list of terms
    query = [term for term in query[0] if term]
    #print(query)

    # query = [posting[0] for posting in query[term]]

    # Initialize docs with the documents containing the first query term
    try:
        docs = set(posting[0] for posting in index[query[0]])
    except KeyError:
        # First term is not in the index
        docs = set()


    for term in query[1:]:
        #print(term, "1")
        try:
            # store in term_docs the ids of the docs that contain "term"
            term_docs = [posting[0] for posting in index[term]]
            #print(f"Query Term: {term}, Matching Docs: {term_docs}")

            # docs = docs Union term_docs --> should be intersection btw query and docs
            docs = docs.intersection(set(term_docs))
        except:
            # term is not in index
            pass

    docs = list(docs)

    ranked_docs, result_scores = rank_documents(query, docs, index, idf, tf)
    return ranked_docs, result_scores


def search_in_corpus(query, _corpus):
    # 1. create create_tfidf_index
    # 2. apply ranking

    num_tweets = len(_corpus)
    lines = []
    for doc_id in _corpus:
        #line = _corpus[doc_id].description
        tweet = _corpus[doc_id].description
        processed_line, url_line = build_terms(tweet)
        line = [doc_id, processed_line]
        lines.append(line)

    index2, tf, df, idf, tweet_index2 = create_index_tfidf(lines, num_tweets)

    ranked_docs, result_scores = search_tf_idf(query, index2, tf, df, idf, tweet_index2)

    return ranked_docs, result_scores
