import psycopg2.extras
from flask import Blueprint, jsonify, request, g

from auth_middleware import token_required
from db_helpers import get_db_connection


saved_directions_blueprint = Blueprint("saved_directions_blueprint", __name__)


MAX_SAVED_DIRECTIONS_PER_USER = 99


def _require_str(value, field_name):
    if value is None:
        raise ValueError(f"Missing required field: {field_name}")
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    return value


def _optional_str(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Expected a string")
    value = value.strip()
    return value if value else None


def _auto_name(origin_label, destination_label):
    o = (origin_label or "").strip() or "Current location"
    d = (destination_label or "").strip() or "Destination"
    return f"{o} → {d}"


@saved_directions_blueprint.route("/saved-directions", methods=["GET"])
@token_required
def index_saved_directions():
    connection = None
    try:
        user_id = g.user["id"]

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """
            SELECT
              id,
              user_id,
              name,
              description,
              origin_label,
              destination_label,
              mode,
              search,
              created_at,
              updated_at
            FROM saved_directions
            WHERE user_id = %s
            ORDER BY updated_at DESC, id DESC;
            """,
            (user_id,),
        )
        rows = cursor.fetchall() or []
        return jsonify(rows), 200
    except Exception as err:
        return jsonify({"err": str(err)}), 500
    finally:
        if connection:
            connection.close()


@saved_directions_blueprint.route("/saved-directions", methods=["POST"])
@token_required
def create_saved_direction():
    connection = None
    try:
        user_id = g.user["id"]
        data = request.get_json() or {}

        search = _require_str(data.get("search"), "search")
        # We store the raw querystring you already use (usually starts with '?').
        if not search.startswith("?"):
            raise ValueError("search must start with '?' (URL querystring)")

        origin_label = _optional_str(data.get("origin_label"))
        destination_label = _optional_str(data.get("destination_label"))
        mode = _optional_str(data.get("mode"))

        name = _optional_str(data.get("name"))
        if not name:
            name = _auto_name(origin_label, destination_label)
        description = _optional_str(data.get("description"))

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            "SELECT COUNT(*)::int AS c FROM saved_directions WHERE user_id = %s;",
            (user_id,),
        )
        count_row = cursor.fetchone() or {"c": 0}
        if int(count_row.get("c", 0)) >= MAX_SAVED_DIRECTIONS_PER_USER:
            return (
                jsonify({"err": f"Saved directions limit reached ({MAX_SAVED_DIRECTIONS_PER_USER})."}),
                400,
            )

        cursor.execute(
            """
            INSERT INTO saved_directions
              (user_id, name, description, origin_label, destination_label, mode, search)
            VALUES
              (%s, %s, %s, %s, %s, %s, %s)
            RETURNING
              id, user_id, name, description, origin_label, destination_label, mode, search, created_at, updated_at;
            """,
            (user_id, name, description, origin_label, destination_label, mode, search),
        )
        created = cursor.fetchone()
        connection.commit()
        return jsonify(created), 201
    except ValueError as ve:
        return jsonify({"err": str(ve)}), 400
    except Exception as err:
        return jsonify({"err": str(err)}), 500
    finally:
        if connection:
            connection.close()


@saved_directions_blueprint.route("/saved-directions/<int:saved_id>", methods=["PUT"])
@token_required
def update_saved_direction(saved_id):
    connection = None
    try:
        user_id = g.user["id"]
        data = request.get_json() or {}

        # All fields optional on update.
        name = _optional_str(data.get("name"))
        description = _optional_str(data.get("description"))
        origin_label = _optional_str(data.get("origin_label"))
        destination_label = _optional_str(data.get("destination_label"))
        mode = _optional_str(data.get("mode"))

        search = data.get("search")
        if search is not None:
            search = _require_str(search, "search")
            if not search.startswith("?"):
                raise ValueError("search must start with '?' (URL querystring)")

        # If name is missing but labels are provided, keep name stable unless explicitly blank.
        if name == "":
            name = _auto_name(origin_label, destination_label)

        sets = []
        vals = []

        def add(field, value):
            if value is None:
                return
            sets.append(f"{field} = %s")
            vals.append(value)

        add("name", name)
        add("description", description)
        add("origin_label", origin_label)
        add("destination_label", destination_label)
        add("mode", mode)
        add("search", search)

        if not sets:
            return jsonify({"err": "No fields provided to update"}), 400

        sets.append("updated_at = NOW()")

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            f"""
            UPDATE saved_directions
            SET {', '.join(sets)}
            WHERE id = %s AND user_id = %s
            RETURNING
              id, user_id, name, description, origin_label, destination_label, mode, search, created_at, updated_at;
            """,
            (*vals, saved_id, user_id),
        )
        updated = cursor.fetchone()
        if not updated:
            return jsonify({"err": "Saved direction not found"}), 404

        connection.commit()
        return jsonify(updated), 200
    except ValueError as ve:
        return jsonify({"err": str(ve)}), 400
    except Exception as err:
        return jsonify({"err": str(err)}), 500
    finally:
        if connection:
            connection.close()


@saved_directions_blueprint.route("/saved-directions/<int:saved_id>", methods=["DELETE"])
@token_required
def delete_saved_direction(saved_id):
    connection = None
    try:
        user_id = g.user["id"]
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """
            DELETE FROM saved_directions
            WHERE id = %s AND user_id = %s
            RETURNING id;
            """,
            (saved_id, user_id),
        )
        deleted = cursor.fetchone()
        if not deleted:
            return jsonify({"err": "Saved direction not found"}), 404
        connection.commit()
        return jsonify(deleted), 200
    except Exception as err:
        return jsonify({"err": str(err)}), 500
    finally:
        if connection:
            connection.close()
