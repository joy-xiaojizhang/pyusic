from app import app, models, db

import flask
import shutil
import os
import youtube_mp3
from urllib.parse import quote

@app.route('/')
def index():
    return "Hello, Pyusic"

def fetch_youtube(uid, options):
    filename = uid + '.mp3'
    filepath = os.path.join(app.static_folder, filename)
    info = youtube_mp3.download(uid, options)
    os.rename(filename, filepath)

    title = flask.request.args.get('title')
    if title is None:
        title = info['title']
    artist = flask.request.args.get('artist')
    if artist is None:
        artist = info['uploader']

    music = models.Music(uid=uid, title=title, artist=artist, web_title=info['title'], uploader=info['uploader'])
    db.session.add(music)
    db.session.commit()
    print('%s added' % uid)

def ensure_existence(uid, options):
    music = models.Music.query.get(uid)
    filename = uid + '.mp3'
    filepath = os.path.join(app.static_folder, filename)

    if music is None:
        print('uid %s not found, redownload' % uid)
    elif not os.path.isfile(filepath):
        print('file %s.mp3 not found, redownload' % uid)
        db.session.delete(music)
        db.session.commit()
    else:
        return music

    fetch_youtube(uid, options)
    music = models.Music.query.get(uid)

    return music

@app.route('/youtube/<uid>')
def youtube(uid):
    title = flask.request.args.get('title')
    artist = flask.request.args.get('artist')
    options = {'title': title, 'artist': artist}

    music = ensure_existence(uid, options)
    
    response = flask.jsonify(music.serialize)
    return response

@app.route('/download/<uid>')
def download(uid):
    title = flask.request.args.get('title')
    artist = flask.request.args.get('artist')
    options = {'title': title, 'artist': artist}

    music = ensure_existence(uid, options)

    if title is None:
        title = music.title
        options['title'] = music.title
    if artist is None:
        artist = music.artist
        options['artist'] = music.artist

    filename = music.uid + '.mp3'
    filepath = os.path.join(app.static_folder, filename)
    tmpfile = '%s - %s.mp3' % (artist, title)
    tmppath = os.path.join(app.static_folder, 'tmp/'+tmpfile) 
    print('Copying %s to %s' % (filename, tmpfile))
    shutil.copyfile(filepath, tmppath)

    youtube_mp3.tag(tmppath, options)

    response = flask.send_from_directory(directory=app.static_folder+'/tmp', filename=tmpfile, as_attachment=True)
    response.headers["Content-Disposition"] = "attachment; filename={}".format(tmpfile.encode().decode('latin-1'))
    return response

@app.route('/modify/<uid>')
def modify(uid):
    title = flask.request.args.get('title')
    artist = flask.request.args.get('artist')
    options = {'title': title, 'artist': artist}

    music = ensure_existence(uid, options)

    if title is None:
        title = music.title
        options['title'] = music.title
    if artist is None:
        artist = music.artist
        options['artist'] = music.artist

    filename = music.uid + '.mp3'
    filepath = os.path.join(app.static_folder, filename)

    youtube_mp3.tag(filepath, options)
    music.title = title
    music.artist = artist
    db.session.commit()

    response = flask.jsonify(music.serialize)
    return response
