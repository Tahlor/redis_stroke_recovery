from pymongo import MongoClient
import xml.etree.ElementTree as ET
from urllib.request import urlopen
import xmltodict
from pathlib import Path
from collections import defaultdict
from dateutil.parser import *

cl = MongoClient()
db = cl["hwr_data"]
#cl.drop_database('hwr_data')
docs = db.docs

from redis import Redis
from rq import Queue

from time import sleep
from pathlib import Path
output_path = Path("./results")

def save_to_hard_drive(the_files):
    """
    Args:
        the_files (tuple): output_file_name, tempfile_path

    Returns:

    """

    file_name, raw_path, rand_token, text, user = the_files
    print(raw_path)

    with Path(raw_path).open("rb") as f:
        data = f.read()
    print(f"Writing data...{rand_token}")
    with (output_path / f"{rand_token}.png").open("wb") as f:
        f.write(data)

    doc = {"file_name":file_name, "raw_path": raw_path, "token":rand_token, "text":text, "user":user}
    docs.insert_one(doc)

if __name__=='__main__':
    # Loop through Queue
    QUEUE = Queue(connection=Redis())
