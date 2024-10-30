from http.client import HTTPException
from typing import Any
from flask import Flask, jsonify, request, g, abort
from random import choice
from pathlib import Path
import sqlite3

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class Base(DeclarativeBase):
    pass

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class QuoteModel(db.Model):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(String(255))
    
    def __init__(self, author, text):
        self.author = author
        self.text = text
    
    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text
        }


@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify(error=e.description), e.code

@app.route("/quotes")
def get_quotes():
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    quotes = []
    for quote in quotes_db:
        quotes.append(quote.to_dict())
    return jsonify(quotes), 200
    
@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id):
    sql = "SELECT * from quotes where id = ?;"
    connection = sqlite3.connect(path_to_db)
    try:
        cursor = connection.cursor()
        cursor.execute(sql, (quote_id, ))
        quotes_db = cursor.fetchall()
    except:
        return jsonify(error="Some database error"), 500
    finally:
        cursor.close()
        connection.close()

    keys = ("id", "author", "text")
    
    quotes = []

    for quote_db in quotes_db:
        quote = dict(zip(keys, quote_db))
        quotes.append(quote)

    return jsonify(quotes), 200
    
@app.route("/quotes", methods=['POST'])
def create_quote():
    
    args = request.json
    author = args.get("author")
    text = args.get("text")

    if (author is None) or (text is None):
        return jsonify(error="Input param error"), 400
    
    sql = "insert into quotes (author, text) values(?, ?);"
    connection = sqlite3.connect(path_to_db)
    try:
        cursor = connection.cursor()
        cursor.execute(sql, (author, text))
        connection.commit()
    except:
        return jsonify(error="Some database error"), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify([]), 200

@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def update_quote(quote_id):
    
    args = request.json
    id = quote_id
    author = args.get("author")
    text = args.get("text")

    if (author is None) or (text is None) or (id is None):
        return jsonify(error="Input param error"), 400
    
    sql = "update quotes set author = ?, text = ? where id = ?;"
    connection = sqlite3.connect(path_to_db)
    try:
        cursor = connection.cursor()
        cursor.execute(sql, (author, text, id))
        connection.commit()
    except:
        return jsonify(error="Some database error"), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify([]), 200

@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id: int):
    id = quote_id

    if (id is None):
        return jsonify(error="Input param error"), 400
    
    sql = "delete from quotes where id = ?;"
    connection = sqlite3.connect(path_to_db)
    try:
        cursor = connection.cursor()
        cursor.execute(sql, (id, ))
        connection.commit()
    except:
        return jsonify(error="Some database error"), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify(message="deleted"), 200


if __name__ == "__main__":
    app.run(debug=True)