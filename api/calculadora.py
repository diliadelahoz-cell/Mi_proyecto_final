from flask import Flask, jsonify, render_template, request
from api.calculadora import calcular_precio

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/calcular-precio", methods=["POST"])
def api_calcular_precio():
    datos = request.get_json(silent=True) or {}
    producto = datos.get("producto", "")
    cantidad_raw = datos.get("cantidad", 1)

    try:
        cantidad = int(cantidad_raw)
    except (TypeError, ValueError):
        return jsonify({
            "ok": False,
            "error": "La cantidad debe ser un número entero válido.",
            "total": 0,
            "total_formateado": "Total: $0",
        }), 400

    resultado = calcular_precio(producto, cantidad)
    codigo_estado = 200 if resultado["ok"] else 400
    return jsonify(resultado), codigo_estado


if __name__ == "__main__":
    app.run(debug=True)