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