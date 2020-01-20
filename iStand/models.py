from iStand import db
from flask_sqlalchemy import SQLAlchemy

# 本情報を格納するテーブル
class Book(db.Model):
    __tablename__ = 'BOOK'
    id = db.Column(db.INTEGER, primary_key=True)
    title = db.Column(db.TEXT)
    isbn = db.Column(db.CHAR(length=13))
    publisher = db.Column(db.TEXT)
    thumbnail = db.Column(db.TEXT)
    regdate = db.Column(db.DATETIME(timezone=True), server_default=db.func.current_timestamp())
    update = db.Column(db.DATETIME(timezone=True), server_onupdate=db.func.current_timestamp() ,server_default=db.func.current_timestamp())
    is_stored = db.Column(db.BOOLEAN)
    block_id = db.Column(db.INTEGER, db.ForeignKey('BLOCK.id'))
    block = db.relationship("Block")
    author = db.relationship("Author")

    def __repr__(self):
        return "<BOOK id={} title={!r} isbn={!r} block={!r} is_stored={!r}>".format(self.id, self.title, self.isbn, self.block_id, self.is_stored)

class Log(db.Model):
    __tablename__ = 'LOG'
    id = db.Column(db.INTEGER, primary_key=True)
    #session = db.Column(db.INTEGER)
    date = db.Column(db.DATETIME(timezone=True), server_default=db.func.current_timestamp())
    book_id = db.Column(db.INTEGER, db.ForeignKey('BOOK.id'))
    book = db.relationship("Book")
    store = db.Column(db.BOOLEAN)
    block_id = db.Column(db.INTEGER, db.ForeignKey('BLOCK.id'))
    block = db.relationship("Block")

class Author(db.Model):
    __tablename__ = 'AUTHOR'
    id = db.Column(db.INTEGER, primary_key=True)    #見せかけ
    book_id = db.Column(db.INTEGER, db.ForeignKey('BOOK.id'))
    author = db.Column(db.TEXT)

class Block(db.Model):
    __tablename__ = 'BLOCK'
    id = db.Column(db.INTEGER, primary_key=True)
    position = db.Column(db.INTEGER)

    def __repr__(self):
        return "<BLOCK id={} position={}>".format(self.id, self.position)

class Motor(db.Model):
    __tablename__ = 'MOTOR'
    id = db.Column(db.INTEGER, primary_key=True)
    frequency = db.Column(db.INTEGER)
    dutycycle = db.Column(db.INTEGER)
    speed = db.Column(db.Float)

'''
class APIParser(db.Model):
    __tablename__ = 'APIPARSER'
    id = db.Column(db.INTEGER, primary_key=True)
    # API名
    name = db.Column(db.TEXT)
    # APIのURL
    url = db.Column(db.TEXT)
    # データタイプ（json，xml，などを指定
    type = db.Column(db.TEXT)
    #以下，apiのどこにデータがあるかをjsonで格納
    title = db.Column(db.TEXT)
    authors = db.Column(db.TEXT)
    isbn = db.Column(db.TEXT)
    publisher = db.Column(db.TEXT)
    detail = db.Column(db.TEXT)
    thumbnail = db.Column(db.TEXT)
    smallthumbnainl = db.Column(db.TEXT)
'''

def CREATE_DATABASE():
    db.create_all()
