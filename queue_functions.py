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
    print("DOING IT!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    file_name, raw_path, rand_token, text, user = the_files
    print(raw_path)

    with Path(raw_path).open("rb") as f:
        data = f.read()
    print(f"Writing data...{rand_token}")
    with (output_path / f"{rand_token}.png").open("wb") as f:
        f.write(data)


if __name__=='__main__':
    # Loop through Queue
    QUEUE = Queue(connection=Redis())
