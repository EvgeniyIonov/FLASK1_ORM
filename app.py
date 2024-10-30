from typing import Any
from flask import Flask, jsonify,request
from random import choice
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "store.db"

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# quotes = [
#    {
#        "id": 3,
#        "author": "Rick Cook",
#        "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
#    },
#    {
#        "id": 5,
#        "author": "Waldi Ravens",
#        "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
#    },
#    {
#        "id": 6,
#        "author": "Mosher’s Law of Software Engineering",
#        "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
#    },
#    {
#        "id": 8,
#        "author": "Yoggi Berra",
#        "text": "В теории, теория и практика неразделимы. На практике это не так."
#    },

# ]

@app.route("/quotes")
def get_quotes():
    sql = "SELECT * from quotes;"
    connection = sqlite3.connect(path_to_db)
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
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

    if (author == None) or (text == None):
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

    if (author == None) or (text == None) or (id == None):
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

    if (id == None):
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

    return jsonify([]), 200


if __name__ == "__main__":
    app.run(debug=True)