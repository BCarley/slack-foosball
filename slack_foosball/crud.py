from sqlalchemy import select
from sqlalchemy.orm import Session

from slack_foosball.models import Game


def get_games(db: Session) -> list[Game]:
    """
    Get entries from matches db
    """
    stmt = select(Game)
    games: list[Game] = []
    for game in db.scalars(stmt):
        games.append(game)
    return games


def create_game(
    db: Session,
    red_attacker: str,
    red_defender: str,
    blue_attacker: str,
    blue_defender: str,
    red_score: int,
    blue_score: int,
    submitted_by: str,
) -> None:
    """
    Get entries from matches db
    """
    game = Game(
        red_attacker=red_attacker,
        red_defender=red_defender,
        red_score=red_score,
        blue_attacker=blue_attacker,
        blue_defender=blue_defender,
        blue_score=blue_score,
        submitted_by=submitted_by,
    )
    db.add(game)
    db.commit()
