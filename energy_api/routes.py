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

@energy_api.route("/analyses", methods=["POST"])
def add_analysis():

    api_key = request.headers.get("X-API-Key")

    if api_key != os.getenv("ENERGY_API_KEY"):
        return jsonify({"error": "unauthorised - wrong key"}), 401

    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body required"}), 400

    article_id = data.get("article_id")
    model = data.get("model")
    prompt_version = data.get("prompt_version")
    title_match = data.get("title_match")
    stocks = data.get("stocks")

    if article_id is None or not model or not prompt_version:
        return jsonify({
            "error": "article_id, model and prompt_version are required"
        }), 400

    if not isinstance(stocks, list):
        return jsonify({
            "error": "stocks must be a list"
        }), 400

    connection = get_energy_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM articles WHERE id = %s",
            (article_id,)
        )

        if cursor.fetchone() is None:
            connection.rollback()
            cursor.close()
            connection.close()

            return jsonify({
                "error": "article not found"
            }), 404

        insert_sql = """
            INSERT INTO analyses (
                article_id,
                symbol,
                sentiment,
                confidence,
                reason,
                model,
                prompt_version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        for stock in stocks:
            cursor.execute(
                insert_sql,
                (
                    article_id,
                    stock.get("symbol"),
                    stock.get("sentiment"),
                    stock.get("confidence"),
                    stock.get("reason"),
                    model,
                    prompt_version
                )
            )

        cursor.execute(
            """
            UPDATE articles
            SET status = 'analysed',
                title_match = %s
            WHERE id = %s
            """,
            (title_match, article_id)
        )

        connection.commit()

    except MySQLdb.IntegrityError:
        connection.rollback()

        cursor.close()
        connection.close()

        return jsonify({
            "error": "analysis conflicts with existing database data"
        }), 409

    except Exception as error:
        connection.rollback()

        print(f"Error saving analysis: {error}")

        cursor.close()
        connection.close()

        return jsonify({
            "error": "failed to save analysis"
        }), 500

    cursor.close()
    connection.close()

    return jsonify({
        "article_id": article_id,
        "status": "analysed",
        "analyses_added": len(stocks)
    }), 201