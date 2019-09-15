import praw
import pickle
from sets import Set
import pdb
import SMS
import datetime
import logging
import configparser

PICKLE_FILE_NAME = "post.pickle"
LOG_FILE_NAME = "watchtracker.log"
CONFIG_FILE_NAME = "config.ini"

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler(LOG_FILE_NAME)
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

config = configparser.ConfigParser()
config.read(CONFIG_FILE_NAME)

def getOrCreateNewCache():
    try:
        with open(PICKLE_FILE_NAME, 'r') as fh:
            postCache = pickle.load(fh)
            if not isinstance(postCache, Set):
                postCache = Set()
    except Exception:
        postCache = Set()
    return postCache

postCache = getOrCreateNewCache()

# This is a blocking function
def trackWatches():
        global postCache
	redditConfig = config['REDDIT']
	client_id = redditConfig['client_id']
	client_secret = redditConfig['client_secret']

	reddit = praw.Reddit(client_id=client_id,
					 client_secret=client_secret,
					 user_agent='Watch Tracker')

        watchesToLookFor = ["ORIS","HYDROCONQUEST","SEAMASTER", "SKX013", "MAX BILL", "C60", "TRIDENT", "OCEAN"]
	for post in reddit.subreddit('watchexchange').stream.submissions():
                if post.id in postCache:
                    logger.info("Post {0} found in cache".format(post.id))
                    continue
		if any(tag in post.title.upper() for tag in watchesToLookFor):
                        postCache.add(post.id)
			postTitle = post.title
			postText = post.selftext
			postDate =  datetime.datetime.fromtimestamp(post.created)
			postRedirectUrl = post.url
			postSelfUrl = reddit.config.reddit_url + post.permalink
			authorComments = []
			for comment in post.comments:
				if comment.author and comment.author.name == post.author.name:
					authorComments.append(comment.body)
			messageContents = "{0} - {1} {2} {3}".format(postTitle.encode('ascii', 'ignore'), postDate, postSelfUrl.encode('ascii', 'ignore'),postText.encode('ascii', 'ignore'))
			SMS.send(messageContents)
			logger.info(messageContents)

def saveCache():
    global postCache
    with open(PICKLE_FILE_NAME, 'wb') as handle:
            pickle.dump(postCache, handle, protocol=pickle.HIGHEST_PROTOCOL)

def main():
    global postCache
    running = True
    while running:
        try:
            trackWatches()
        except KeyboardInterrupt:
            logger.info("Keyboard terminate received")
            running = False
        except Exception as e:
            logger.exception('run loop exeption: {0}'.format(e))
            time.sleep(10)
            SMS.send("Something went wrong with WatchTracker :(")
        finally:
            saveCache()


if __name__== "__main__":
    main()
