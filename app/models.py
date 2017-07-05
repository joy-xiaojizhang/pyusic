from app import db

class Music(db.Model):
    uid = db.Column(db.String(16), primary_key=True, index=True, unique=True)
    web_title = db.Column(db.String(128))
    uploader = db.Column(db.String(32))
    title = db.Column(db.String(128))
    artist = db.Column(db.String(32))

    @property
    def serialize(self):
        return {
                'uid': self.uid,
                'web_title': self.web_title,
                'uploader': self.uploader,
                'title': self.title,
                'artist': self.artist}
