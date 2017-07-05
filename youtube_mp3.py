from __future__ import unicode_literals

import eyed3
import os
import youtube_dl

def tag(filename, info):
    audio = eyed3.load(filename)
    audio.tag.artist = info['artist']
    audio.tag.title = info['title']
    audio.tag.save()

def download(url, info={}):
    options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            }],
        }

    with youtube_dl.YoutubeDL(options) as ydl:
        youtube_info = ydl.extract_info(url, download=False)
        ydl.download([url])
        filename = youtube_info.get('id', None) + '.mp3'
        if 'artist' not in info or info['artist'] is None:
            info['artist'] = youtube_info['uploader']
        if 'title' not in info or info['title'] is None:
            info['title']  = youtube_info['title']
        tag(filename, info)

        if 'friendly_name' in info and info['friendly_name'] is True:
            newname = '%s - %s.mp3' % (info['artist'], info['title'])
            os.rename(filename, newname)
            filename = newname

        return {'filename': filename,
                'id': youtube_info['id'],
                'uploader': youtube_info['uploader'],
                'title': youtube_info['title']}
