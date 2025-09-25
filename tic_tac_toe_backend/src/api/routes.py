"""Tic Tac Toe API routes.

Ocean Professional style: Clear summaries, detailed descriptions,
and consistent response envelopes.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path

from ..models.game_models import (
    ErrorResponse,
    GameStatus,
    GameStatusResponse,
    MoveRequest,
    MoveResponse,
    NewGameResponse,
)
from ..services.game_service import store, available_moves

router = APIRouter(prefix="/api/v1/tictactoe", tags=["Tic Tac Toe"])


# PUBLIC_INTERFACE
@router.post(
    "/games",
    summary="Start a new game",
    description="Create a new Tic Tac Toe game session and return its initial state.",
    response_model=NewGameResponse,
    responses={
        201: {"description": "Game successfully created"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    status_code=201,
)
def start_game() -> NewGameResponse:
    """Create a new game and return initial state."""
    game = store.create()
    return NewGameResponse(
        game_id=game.game_id,
        board=game.board.to_display_rows(),
        next_player=game.next_player,
        status=game.status,
        winner=game.winner,
    )


# PUBLIC_INTERFACE
@router.get(
    "/games/{game_id}",
    summary="Get game status",
    description="Fetch the current status and board for a specific game.",
    response_model=GameStatusResponse,
    responses={
        200: {"description": "Current game status"},
        404: {"model": ErrorResponse, "description": "Game not found"},
    },
)
def get_game_status(
    game_id: str = Path(..., description="Identifier of the game to fetch."),
) -> GameStatusResponse:
    """Return up-to-date status for the game with the given id."""
    game = store.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameStatusResponse(
        game_id=game.game_id,
        board=game.board.to_display_rows(),
        next_player=game.next_player if game.status == GameStatus.IN_PROGRESS else None,
        status=game.status,
        winner=game.winner,
        available_moves=available_moves(game) if game.status == GameStatus.IN_PROGRESS else [],
    )


# PUBLIC_INTERFACE
@router.post(
    "/games/{game_id}/moves",
    summary="Make a move",
    description="Apply a move at the specified row and column for the current player.",
    response_model=MoveResponse,
    responses={
        200: {"description": "Move applied"},
        400: {"model": ErrorResponse, "description": "Invalid move"},
        404: {"model": ErrorResponse, "description": "Game not found"},
        409: {"model": ErrorResponse, "description": "Game already finished"},
    },
)
def make_move(
    payload: MoveRequest,
    game_id: str = Path(..., description="Identifier of the game to update."),
) -> MoveResponse:
    """Apply a move to the given game. Returns updated game state."""
    game = store.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="Game is already finished")

    try:
        game.place(payload.row, payload.col)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    message = "Move accepted."
    if game.status == GameStatus.DRAW:
        message = "Game ended in a draw."
    elif game.status == GameStatus.X_WON:
        message = "Player X won. Congratulations!"
    elif game.status == GameStatus.O_WON:
        message = "Player O won. Congratulations!"

    return MoveResponse(
        game_id=game.game_id,
        board=game.board.to_display_rows(),
        next_player=game.next_player if game.status == GameStatus.IN_PROGRESS else None,
        status=game.status,
        winner=game.winner,
        message=message,
    )
