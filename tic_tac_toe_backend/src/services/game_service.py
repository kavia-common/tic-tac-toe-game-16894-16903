"""Service layer for Tic Tac Toe.

Contains game repository and orchestration logic.
"""
from __future__ import annotations

import uuid
from typing import Dict, List, Optional, Tuple

from ..models.game_models import Game


class InMemoryGameStore:
    """A very simple in-memory game store keyed by game_id."""
    def __init__(self) -> None:
        self._games: Dict[str, Game] = {}

    def create(self) -> Game:
        game_id = uuid.uuid4().hex
        game = Game(game_id=game_id)
        self._games[game_id] = game
        return game

    def get(self, game_id: str) -> Optional[Game]:
        return self._games.get(game_id)

    def all_ids(self) -> List[str]:
        return list(self._games.keys())


# Singleton store for the app process lifetime
store = InMemoryGameStore()


def available_moves(game: Game) -> List[Tuple[int, int]]:
    """Return a list of all empty cells as (row, col) pairs."""
    moves: List[Tuple[int, int]] = []
    for r in range(3):
        for c in range(3):
            if game.board.empty_at(r, c):
                moves.append((r, c))
    return moves
