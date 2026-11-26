import html
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs


PRODUCTOS = {
    "llave": {
        "nombre": "Duplicado de llave",
        "precio": 4500
    },
    "candado": {
        "nombre": "Candado",
        "precio": 55000
    },
    "llavero": {
        "nombre": "Llavero",
        "precio": 3500
    }
}


def formatear_pesos(valor):
    return "$" + f"{valor:,.0f}".replace(",", ".")


def calcular_precio(producto_id, cantidad):
    if producto_id not in PRODUCTOS:
        return {
            "ok": False,
            "mensaje": "Selecciona un producto válido."
        }

    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "mensaje": "La cantidad debe ser un número entero válido."
        }

    if cantidad < 1:
        return {
            "ok": False,
            "mensaje": "La cantidad debe ser al menos 1."
        }

    producto = PRODUCTOS[producto_id]

    subtotal = producto["precio"] * cantidad

    return {
        "ok": True,
        "producto": producto["nombre"],
        "cantidad": cantidad,
        "precio_unitario": formatear_pesos(producto["precio"]),
        "total": formatear_pesos(subtotal)
    }


def crear_pagina(contenido):
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resultado | Cerrajería Dany</title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 25px 15px;
            font-family: Arial, sans-serif;
            background: #f2f2f2;
            color: #333;
        }}

        .contenedor {{
            max-width: 520px;
            margin: 40px auto;
            padding: 30px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}

        h1 {{
            text-align: center;
            color: #333;
        }}

        .detalle {{
            padding: 13px 0;
            border-bottom: 1px solid #ddd;
        }}

        .total {{
            margin-top: 25px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: #16743b;
        }}

        .mensaje {{
            margin-top: 20px;
            padding: 15px;
            background: #f0f5f0;
            border-radius: 8px;
            text-align: center;
        }}

        .boton {{
            display: block;
            margin-top: 25px;
            padding: 13px;
            background: #333;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 7px;
        }}

        .boton:hover {{
            background: #555;
        }}
    </style>
</head>

<body>

    <main class="contenedor">

        {contenido}

        <a href="/" class="boton">
            Volver a Cerrajería Dany
        </a>

    </main>

</body>
</html>"""


class handler(BaseHTTPRequestHandler):

    def enviar_pagina(self, contenido, estado=200):
        pagina = crear_pagina(contenido)

        self.send_response(estado)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        self.wfile.write(pagina.encode("utf-8"))

    def do_GET(self):
        contenido = """
        <h1>🔑 Cerrajería Dany</h1>
        <p>Para calcular el precio, regresa a la página principal
        y completa el formulario.</p>
        """

        self.enviar_pagina(contenido)

    def do_POST(self):
        longitud = int(self.headers.get("Content-Length", 0))

        datos_recibidos = self.rfile.read(longitud).decode("utf-8")

        datos = parse_qs(datos_recibidos)

        producto = datos.get("producto", [""])[0]
        cantidad = datos.get("cantidad", [""])[0]

        resultado = calcular_precio(producto, cantidad)

        if not resultado["ok"]:
            mensaje = html.escape(resultado["mensaje"])

            contenido = f"""
            <h1>No se pudo calcular</h1>
            <div class="mensaje">{mensaje}</div>
            <p>Regresa al formulario e intenta nuevamente.</p>
            """

            self.enviar_pagina(contenido, 400)
            return

        nombre = html.escape(resultado["producto"])
        cantidad = resultado["cantidad"]
        precio = resultado["precio_unitario"]
        total = resultado["total"]

        contenido = f"""
        <h1>🔑 Cerrajería Dany</h1>

        <h2>Resumen de tu compra</h2>

        <div class="detalle">
            <strong>Producto:</strong> {nombre}
        </div>

        <div class="detalle">
            <strong>Cantidad:</strong> {cantidad}
        </div>

        <div class="detalle">
            <strong>Precio por unidad:</strong> {precio}
        </div>

        <div class="total">
            Total: {total}
        </div>

        <div class="mensaje">
            Este es el valor estimado de tu compra.
            Para confirmar disponibilidad, comunícate con nosotros.
        </div>
        """

        self.enviar_pagina(contenido)