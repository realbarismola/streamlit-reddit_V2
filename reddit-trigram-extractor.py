import subprocess

# Install the necessary packages
subprocess.call(['pip', 'install', 'praw'])
subprocess.call(['pip', 'install', 'nltk'])
subprocess.call(['pip', 'install', 'gensim'])
subprocess.call(['pip', 'install', 'streamlit'])

import time
import praw
import nltk
import gensim
from nltk.corpus import stopwords
from collections import Counter
from itertools import tee, islice
import concurrent.futures

import nltk
nltk.download('punkt')
nltk.download('stopwords')
import streamlit as st

st.title('Reddit Topic Finder')

def preprocess(posts):
    # Combine the title and body of each post and preprocess the text
    text = ''
    for post in posts:
        text += post.title + ' ' + post.selftext + ' '
    words = nltk.word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.isalpha() and word not in stop_words]
    return words

def trigram_generator(words):
    # Use a generator to extract trigrams from the preprocessed text
    trigrams = zip(words, islice(words, 1, None), islice(words, 2, None))
    for trigram in trigrams:
        yield trigram

def count_trigrams(trigram_gen):
    # Use a counter to count the frequency of each trigram
    trigram_dict = Counter()
    for trigram in trigram_gen:
        trigram_dict[trigram] += 1
    return trigram_dict

def main():
    start_time = time.time()
    # Set up the Reddit API connection
    reddit = praw.Reddit(client_id='nrGPL_tS8GZIp8ccFFDodw',
                         client_secret='j8KG735o7cN_h-DPdNdePekW7FL5tg',
                         user_agent='OldSchoolHaze68')

    # Prompt the user to enter the name of the subreddit to analyze
    subreddit_name = st.text_input('Enter the name of the subreddit to analyze')

    # Wait for the user to enter a subreddit name before proceeding
    if not subreddit_name:
        return

    try:
        # Get the top posts from the subreddit
        subreddit = reddit.subreddit(subreddit_name)
        all_posts = subreddit.top(limit=None)

        # Preprocess the text
        words = preprocess(all_posts)

        # Use multiprocessing to count the trigrams in parallel
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Split the words into chunks for processing in parallel
            chunk_size = 10000
            chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
            # Process each chunk in parallel and combine the results
            trigram_counts = Counter()
            for chunk_trigram_counts in executor.map(count_trigrams, map(trigram_generator, chunks)):
                trigram_counts += chunk_trigram_counts

        # Remove trigrams that contain stop words
        stop_words = set(stopwords.words('english'))
        for trigram in list(trigram_counts):
            if any(word in stop_words for word in trigram):
                del trigram_counts[trigram]

        # Print the top 10 most common trigrams
        st.write('Top 10 most common trigrams:')
        for trigram, count in trigram_counts.most_common(10):
            st.write(f'{trigram} ({count} occurrences)')

    except Exception as e:
        st.write(f'Error: {e}')

    # Measure the elapsed time and display it to the user
    elapsed_time = time.time() - start_time
    st.write(f'Time elapsed: {elapsed_time:.2f} seconds')

if __name__ == '__main__':
    main()
