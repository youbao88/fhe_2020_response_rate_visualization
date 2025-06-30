from app import app  # import your Dash app object
import os

server = app.server  # Flask server instance

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port)