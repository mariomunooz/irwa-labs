import random

from myapp.search.algorithms import search_in_corpus
from myapp.search.objects import ResultItem, Document



def build_demo_results_given_toy(corpus: dict, search_id,search_query):
    """
    Helper method, just to demo the app
    :return: a list of demo docs sorted by ranking
    """
    res = []
    size = len(corpus)

    ll = list(corpus.values())

    for index in range(random.randint(0, 40)):
        # Getting a random object in the list of documents
        item: Document = ll[random.randint(0, size)] 

        #if you want to search if the search query is in the quote
        if search_query in item.quote.split():
            res.append(ResultItem(item.id, item.title, item.description, item.doc_date,
                                  "doc_details?id={}&search_id={}".format(item.id, search_id), random.random()))


        #generate total random results
        #res.append(ResultItem(item.id, item.author, item.quote,random.randint(0, size)))

    # simulate sort by ranking
    res.sort(key=lambda doc: doc.ranking, reverse=True)
    return res


def build_demo_results(corpus: dict, search_id):
    """
    Helper method, just to demo the app
    :return: a list of demo docs sorted by ranking
    """
    res = []
    size = len(corpus)
    ll = list(corpus.values())
    for index in range(random.randint(0, 40)):
        item: Document = ll[random.randint(0, size)]
        res.append(ResultItem(item.id, item.title, item.description, item.doc_date,
                              "doc_details?id={}&search_id={}&param2=2".format(item.id, search_id), random.random()))

    # for index, item in enumerate(corpus['Id']):
    #     # DF columns: 'Id' 'Tweet' 'Username' 'Date' 'Hashtags' 'Likes' 'Retweets' 'Url' 'Language'
    #     res.append(DocumentInfo(item.Id, item.Tweet, item.Tweet, item.Date,
    #                             "doc_details?id={}&search_id={}&param2=2".format(item.Id, search_id), random.random()))

    # simulate sort by ranking
    res.sort(key=lambda doc: doc.ranking, reverse=True)
    return res


class SearchEngine:
    """educational search engine"""

    def search(self, search_query, search_id, _corpus):
        print("Search query:", search_query)

        results = []
        ##### your code here #####
        # results = build_demo_results(corpus, search_id)  # replace with call to search algorithm
        results, ranked_documents = search_in_corpus(search_query, _corpus)

        return results, ranked_documents

      #  return [ResultItem(item.id, item.title, item.description, item.doc_date,
      #                     "doc_details?id={}&search_id={}&param2=2".format(item.id, search_id), score)
      #          for item, score in zip(documents, results)]
