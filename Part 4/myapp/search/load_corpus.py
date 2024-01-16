import pandas as pd
import numpy as np
import json
from myapp.search.objects import Document
from myapp.core.utils import load_json_file
from pandas import json_normalize

_corpus = {}

def document_to_dataframe(corpus):
    """
    data_list = []

    for tweet_id, document in corpus.items():
        article_id = document.id
        tweet_text = document.description
        date = document.doc_date
        likes = document.likes
        retweets = document.retweets
        url = document.url
        hashtags = document.hashtags
        title = document.title

        data_list.append({
            'Tweet_Id': tweet_id,
            'Tweet_Text': tweet_text,
            'Date': date,
            'Likes': likes,
            'Retweets': retweets,
            'Url': url,
            'Hashtags': hashtags,
            "Title" : title

        })
    """
    data_list = [
        {
            'Tweet_Id': tweet_id,
            'Tweet_Text': document.description,
            'Date': document.doc_date,
            'Likes': document.likes,
            'Retweets': document.retweets,
            'Url': document.url,
            'Hashtags': document.hashtags,
            "Title": document.title
        }
        for tweet_id, document in corpus.items()
    ]


# Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data_list)
    return df


def load_corpus(path) -> [Document]:
    """
        Load file and transform to dictionary with each document as an object for easier treatment when needed for displaying
         in results, stats, etc.
        :param path:
        :return:
    """

    # Own approach: read json file into dataframe
    df = pd.read_json(path, lines=True)
    corpus_data = []

    for index, row in df.iterrows():
        doc_id = row.get('doc_id')
        if doc_id is not None:
            #_corpus[doc_id] = Document(
                #doc_id,
                #row['full_text'][0:100],  # Adjust the slicing as needed
                #row['full_text'],
                #row['created_at'],
                #row['favorite_count'],
                #row['retweet_count'],
                #'https://twitter.com/' + row['user']['screen_name'] + '/status' + str(doc_id),
                #[tag['text'] for tag in row.get('entities', {}).get('hashtags', [])]
                # Add other fields as needed
            #)

            document = Document(
                doc_id,
                row['full_text'][0:100],  # Adjust the slicing as needed
                row['full_text'],
                row['created_at'],
                row['favorite_count'],
                row['retweet_count'],
                'https://twitter.com/' + row['user']['screen_name'] + '/status' + str(doc_id),
                [tag['text'] for tag in row.get('entities', {}).get('hashtags', [])]
                # Add other fields as needed
            )
            corpus_data.append((doc_id, document))

    _corpus = dict(corpus_data)
    #_corpus.apply(_row_to_doc_dict, axis=1)
    return _corpus


def _load_corpus_as_dataframe(path):
    """
    Load documents corpus from file in 'path'
    :return:
    """
    json_data = load_json_file(path)
    tweets_df = _load_tweets_as_dataframe(json_data)
    _clean_hashtags_and_urls(tweets_df)
    # Rename columns to obtain: Tweet | Username | Date | Hashtags | Likes | Retweets | Url | Language
    corpus = tweets_df.rename(
        columns={"id": "Id", "full_text": "Tweet", "screen_name": "Username", "created_at": "Date",
                 "favorite_count": "Likes",
                 "retweet_count": "Retweets", "lang": "Language"})

    # select only interesting columns
    filter_columns = ["Id", "Tweet", "Username", "Date", "Hashtags", "Likes", "Retweets", "Url", "Language"]
    corpus = corpus[filter_columns]
    return corpus


def _load_tweets_as_dataframe(json_data):
    data = pd.DataFrame(json_data).transpose()
    # parse entities as new columns
    data = pd.concat([data.drop(['entities'], axis=1), data['entities'].apply(pd.Series)], axis=1)
    # parse user data as new columns and rename some columns to prevent duplicate column names
    data = pd.concat([data.drop(['user'], axis=1), data['user'].apply(pd.Series).rename(
        columns={"created_at": "user_created_at", "id": "user_id", "id_str": "user_id_str", "lang": "user_lang"})],
                     axis=1)
    return data


def _build_tags(row):
    tags = []
    # for ht in row["hashtags"]:
    #     tags.append(ht["text"])
    for ht in row:
        tags.append(ht["text"])
    return tags



def _build_url(row):
    url = ""
    try:
        url = row["entities"]["url"]["urls"][0]["url"]  # tweet URL
    except:
        try:
            url = row["retweeted_status"]["extended_tweet"]["entities"]["media"][0]["url"]  # Retweeted
        except:
            url = ""
    return url


def _clean_hashtags_and_urls(df):
    #df["Hashtags"] = df["hashtags"].apply(_build_tags)
    df["Hashtags"] = df["entities.hashtags"].apply(_build_tags)
    df["Url"] = df.apply(lambda row: _build_url(row), axis=1)
    # df["Url"] = "TODO: get url from json"
    df.drop(columns=["entities"], axis=1, inplace=True)


def load_tweets_as_dataframe2(json_data):
    """Load json into a dataframe

    Parameters:
    path (string): the file path

    Returns:
    DataFrame: a Panda DataFrame containing the tweet content in columns
    """
    # Load the JSON as a Dictionary
    tweets_dictionary = json_data.items()
    # Load the Dictionary into a DataFrame.
    dataframe = pd.DataFrame(tweets_dictionary)
    # remove first column that just has indices as strings: '0', '1', etc.
    dataframe.drop(dataframe.columns[0], axis=1, inplace=True)
    return dataframe


def load_tweets_as_dataframe3(json_data):
    """Load json data into a dataframe

    Parameters:
    json_data (string): the json object

    Returns:
    DataFrame: a Panda DataFrame containing the tweet content in columns
    """

    # Load the JSON object into a DataFrame.
    dataframe = pd.DataFrame(json_data).transpose()

    # select only interesting columns
    filter_columns = ["id", "full_text", "created_at", "entities", "retweet_count", "favorite_count", "lang"]
    dataframe = dataframe[filter_columns]
    return dataframe


def _row_to_doc_dict(row: pd.Series):
    _corpus[row['Id']] = Document(row['Id'], row['Tweet'][0:100], row['Tweet'], row['Date'], row['Likes'],
                                 row['Retweets'],
                                 row['Url'], row['Hashtags'])


