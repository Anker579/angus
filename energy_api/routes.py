import os
import MySQLdb
from flask import Blueprint, jsonify, request
from energy_api.database import get_energy_db_connection

energy_api = Blueprint("energy_api", __name__)


@energy_api.route("/ping")
def ping():
    return jsonify({"message": "energy api working"})

@energy_api.route("/articles/check")
def check_article():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "url parameter is required"}), 400

    connection = get_energy_db_connection()
    cursor = connection.cursor()

    sql = """
        SELECT id, status
        FROM articles
        WHERE url = %s
        LIMIT 1
    """

    cursor.execute(sql, (url,))
    article = cursor.fetchone()

    cursor.close()
    connection.close()

    if article:
        return jsonify({
            "exists": True,
            "article_id": article[0],
            "status": article[1]
        })

    return jsonify({
        "exists": False
    })

@energy_api.route("/articles", methods=["POST"])
def add_article():

    api_key = request.headers.get("X-API-Key")

    if api_key != os.getenv("ENERGY_API_KEY"):
        return jsonify({"error": "unauthorised - wrong key"}), 401

    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body required"}), 400

    url = data.get("url")
    title = data.get("title")
    publisher = data.get("publisher")
    source_api = data.get("source_api")
    published_at = data.get("published_at")

    if not url or not title:
        return jsonify({
            "error": "url and title are required"
        }), 400

    connection = get_energy_db_connection()
    cursor = connection.cursor()

    sql = """
        INSERT INTO articles (
            url,
            title,
            publisher,
            source_api,
            published_at,
            status
        )
        VALUES (%s, %s, %s, %s, %s, 'pending')
    """

    try:
        cursor.execute(
            sql,
            (
                url,
                title,
                publisher,
                source_api,
                published_at
            )
        )

        connection.commit()

        article_id = cursor.lastrowid

    except MySQLdb.IntegrityError:
        connection.rollback()

        cursor.close()
        connection.close()

        return jsonify({
            "error": "article already exists"
        }), 409

    cursor.close()
    connection.close()

    return jsonify({
        "article_id": article_id,
        "status": "pending"
    }), 201