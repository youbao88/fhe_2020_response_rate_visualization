from app import app  # import your Dash app object

server = app.server  # Flask server instance

if __name__ == "__main__":
    server.run()