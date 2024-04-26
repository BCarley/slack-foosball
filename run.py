import os

from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_foosball import database
from slack_foosball.app import app
from slack_foosball.database import Base

DB = "games.db"
__all__ = ["Base"]
if __name__ == "__main__":
    database.init_db(DB)
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
