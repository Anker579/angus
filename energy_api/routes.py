from flask import Blueprint, jsonify

energy_api = Blueprint("energy_api", __name__)


@energy_api.route("/ping")
def ping():
    return jsonify({"message": "energy api working"})