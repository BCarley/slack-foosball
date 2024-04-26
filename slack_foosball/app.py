import logging
import os
from typing import Any, Optional

from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from slack_foosball import crud, database, models

# Initialization
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

manager = database.DBManager()


def build_games_table() -> str:
    """
    Build games table
    """


@app.event("app_home_opened")
def update_home_tab(body, client, event, logger, ack):
    with manager() as db:
        games = crud.get_games(db)

    view = {
        "type": "home",
        "callback_id": "home_view",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Recent Matches* :soccer:",
                },
            },
        ],
    }
    if games:
        view["blocks"].append({"type": "divider"})

    for game in games:
        red_prize = blue_prize = ""
        if game.blue_score > game.red_score:
            blue_prize = ":trophy:"
        elif game.blue_score < game.red_score:
            red_prize = ":trophy:"
        date = game.played_at.strftime("%Y-%m-%d %H:%M")
        view["blocks"].extend(
            [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*:clock1: Date:* `{date}`"},
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":red_circle: {game.red_score} - {game.blue_score} :large_blue_circle:",
                    },
                },
            ]
        )
        view["blocks"].append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":red_circle:  <@{game.red_attacker}> & <@{game.red_defender}> {red_prize} ",
                },
            }
        )
        view["blocks"].append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":large_blue_circle:  <@{game.blue_attacker}> & <@{game.blue_defender}> {blue_prize}",
                },
            }
        )

    user_email = lookup_user(client, body["event"]["user"])
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view=view,
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@app.command("/hello-bolt-python")
def handle_command(body, ack, client, logger):
    logger.info(body)
    ack()

    res = client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "create-game",
            "title": {
                "type": "plain_text",
                "text": "Record Game",
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Red Attacker"},
                    "accessory": {
                        "type": "users_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a user",
                            "emoji": True,
                        },
                        "action_id": "red-attacker",
                    },
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Red Defender"},
                    "accessory": {
                        "type": "users_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a user",
                            "emoji": True,
                        },
                        "action_id": "red-defender",
                    },
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Blue Attacker"},
                    "accessory": {
                        "type": "users_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a user",
                            "emoji": True,
                        },
                        "action_id": "blue-attacker",
                    },
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Blue Defender"},
                    "accessory": {
                        "type": "users_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a user",
                            "emoji": True,
                        },
                        "action_id": "blue-defender",
                    },
                },
                {
                    "type": "input",
                    "element": {
                        "type": "number_input",
                        "is_decimal_allowed": False,
                        "action_id": "red-score",
                        "min_value": "0",
                        "max_value": "9",
                    },
                    "label": {"type": "plain_text", "text": "Red Score", "emoji": True},
                },
                {
                    "type": "input",
                    "element": {
                        "type": "number_input",
                        "is_decimal_allowed": False,
                        "action_id": "blue-score",
                        "min_value": "0",
                        "max_value": "9",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Blue Score",
                        "emoji": True,
                    },
                },
            ],
        },
    )
    logger.info(res)


def lookup_user(client: WebClient, user_id: str) -> Optional[str]:
    """
    Lookup a user by user_id.

    Args:
        email: slack users email
    Returns:
        None if user is not found
        UserId if found, the user ID can be used as a channel
    """
    try:
        data = client.users_info(user=user_id).data
    except SlackApiError:
        logging.warning(f"Unable to lookup username: `{user_id}`", exc_info=True)
        return None

    if isinstance(data, bytes):
        return None

    try:
        return data["user"]["profile"]["email"]
    except KeyError:
        return None


@app.action("red-attacker")
@app.action("red-defender")
@app.action("blue-attacker")
@app.action("blue-defender")
def ack_selections(ack):
    ack()


@app.action("red-score")
@app.action("blue-score")
def ack_scores(ack):
    ack()


@app.view("create-game")
def view_submission(ack, body, logger):
    ack()
    logger.info(body["view"]["state"]["values"])
    values = {}
    for value in body["view"]["state"]["values"].values():
        values.update(value)

    game: dict[str, Any] = dict(
        red_attacker=values["red-attacker"]["selected_user"],
        red_defender=values["red-attacker"]["selected_user"],
        blue_attacker=values["blue-attacker"]["selected_user"],
        blue_defender=values["blue-defender"]["selected_user"],
        red_score=int(values["red-score"]["value"]),
        blue_score=int(values["blue-score"]["value"]),
        submitted_by=body["user"]["id"],
    )
    with manager() as db:
        crud.create_game(db, **game)
