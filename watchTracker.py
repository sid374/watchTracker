import praw
import pdb
import SMS
import datetime
import logging
import configparser

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("watchtracker.log")
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

config = configparser.ConfigParser()
config.read('config.ini')

# This is a blocking function
def trackWatches():
	redditConfig = config['REDDIT']
	client_id = redditConfig['client_id']
	client_secret = redditConfig['client_secret']

	reddit = praw.Reddit(client_id=client_id,
					 client_secret=client_secret,
					 user_agent='Watch Tracker')

	watchesToLookFor = ["ORIS"]
	for post in reddit.subreddit('watchexchange').stream.submissions():
		if any(tag in post.title.upper() for tag in watchesToLookFor):
			postTitle = post.title
			postText = post.selftext
			postDate =  datetime.datetime.fromtimestamp(post.created)
			postRedirectUrl = post.url
			postSelfUrl = reddit.config.reddit_url + post.permalink
			authorComments = []
			for comment in post.comments:
				if comment.author and comment.author.name == post.author.name:
					authorComments.append(comment.body)
			messageContents = "{0} - {1} {2} {3}".format(postTitle, postDate, postText, postSelfUrl)
			SMS.send(messageContents)
			logger.info(messageContents)


trackWatches()
