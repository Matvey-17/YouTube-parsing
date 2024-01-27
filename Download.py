import ssl

from pytube import YouTube

from path_download import path
from DB import DbConnect


def download(url, chat_id):
    ssl._create_default_https_context = ssl._create_unverified_context

    yt = YouTube(url)
    if (yt.streams.get_highest_resolution().filesize / 1048576) <= 50:
        video = yt.streams.first().download(path)
        db_add_url = DbConnect(chat_id)
        db_add_url.add_url(video)
    else:
        db_add_url = DbConnect(chat_id)
        db_add_url.add_url('None')
