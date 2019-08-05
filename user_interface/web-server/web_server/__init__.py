import os
import logging

from quart import request, jsonify
from quart_openapi import Pint, Resource
from quart_cors import cors

# -----------------------------------------------------------------------------

logger = logging.getLogger("web_interface")

def make_app():
    app = Pint(__name__, title="Rhasspy")
    app = cors(app)

    @app.route("/")
    class Root(Resource):
        async def get(self):
            """Hello World Route

        This docstring will show up as the description and short-description
        for the openapi docs for this route.
        """
            return "hello"


    @app.websocket("/ws")
    async def ws():
        while True:
            await websocket.send("hello")


