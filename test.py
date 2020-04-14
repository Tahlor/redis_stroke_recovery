from redis import Redis
from rq import Queue
from my_module import count_words_at_url


q = Queue(connection=Redis())
result = q.enqueue(count_words_at_url, 'http://nvie.com')
