"""Domain models and DTOs for the Tic Tac Toe FastAPI backend.

Ocean Professional style: Clean, modern, well-documented types.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, model_validator


class Player(str, Enum):
    """Represents a player marker on the Tic Tac Toe board."""
    X = "X"
    O = "O"


class CellState(str, Enum):
    """State of a cell on the board."""
    EMPTY = " "
    X = "X"
    O = "O"


class GameStatus(str, Enum):
    """Lifecycle state of a game."""
    IN_PROGRESS = "IN_PROGRESS"
    X_WON = "X_WON"
    O_WON = "O_WON"
    DRAW = "DRAW"


class Board(BaseModel):
    """3x3 Tic Tac Toe board abstraction using a flat 9-length list."""
    cells: List[CellState] = Field(
        default_factory=lambda: [CellState.EMPTY] * 9,
        description="Flat list length 9, row-major order (indices 0..8)."
    )

    def index(self, row: int, col: int) -> int:
        """Calculate the flat index for a row/col pair."""
        return row * 3 + col

    def get(self, row: int, col: int) -> CellState:
        """Get the state at a specific cell."""
        return self.cells[self.index(row, col)]

    def set(self, row: int, col: int, value: CellState) -> None:
        """Set the state at a specific cell."""
        self.cells[self.index(row, col)] = value

    def is_full(self) -> bool:
        """Return True if no empty cells remain."""
        return all(c != CellState.EMPTY for c in self.cells)

    def empty_at(self, row: int, col: int) -> bool:
        """Return True if the cell (row,col) is empty."""
        return self.get(row, col) == CellState.EMPTY

    def to_display_rows(self) -> List[List[str]]:
        """Return the board as 3 rows of display-friendly strings."""
        return [
            [self.get(r, c).value for c in range(3)]
            for r in range(3)
        ]


class Game(BaseModel):
    """Aggregate root for a Tic Tac Toe game session."""
    game_id: str = Field(..., description="Unique identifier for the game.")
    board: Board = Field(default_factory=Board, description="3x3 board state.")
    next_player: Player = Field(default=Player.X, description="Player whose turn it is.")
    status: GameStatus = Field(default=GameStatus.IN_PROGRESS, description="Current game status.")
    winner: Optional[Player] = Field(default=None, description="Winner if any.")

    def place(self, row: int, col: int) -> None:
        """Place the current player's mark on the board at (row, col)."""
        if self.status != GameStatus.IN_PROGRESS:
            raise ValueError("Game is already finished.")
        if not (0 <= row <= 2 and 0 <= col <= 2):
            raise ValueError("Row and column must be within [0, 2].")
        if not self.board.empty_at(row, col):
            raise ValueError("Cell is already occupied.")

        mark = CellState.X if self.next_player == Player.X else CellState.O
        self.board.set(row, col, mark)

        # Update status
        winner = self._compute_winner()
        if winner is not None:
            self.status = GameStatus.X_WON if winner == Player.X else GameStatus.O_WON
            self.winner = winner
        elif self.board.is_full():
            self.status = GameStatus.DRAW
        else:
            self.next_player = Player.O if self.next_player == Player.X else Player.X

    def _compute_winner(self) -> Optional[Player]:
        """Compute winner from current board, if any."""
        lines: List[Tuple[int, int, int]] = [
            # Rows
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            # Cols
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            # Diagonals
            (0, 4, 8), (2, 4, 6),
        ]
        for a, b, c in lines:
            trio = (self.board.cells[a], self.board.cells[b], self.board.cells[c])
            if trio[0] != CellState.EMPTY and trio[0] == trio[1] == trio[2]:
                return Player.X if trio[0] == CellState.X else Player.O
        return None


# PUBLIC_INTERFACE
class NewGameResponse(BaseModel):
    """Response model when a new game is created."""
    game_id: str = Field(..., description="Newly created game identifier.")
    board: List[List[str]] = Field(..., description="Current board in rows for display.")
    next_player: Player = Field(..., description="Next player to move.")
    status: GameStatus = Field(..., description="Game status.")
    winner: Optional[Player] = Field(default=None, description="Winner if any.")


# PUBLIC_INTERFACE
class MoveRequest(BaseModel):
    """Request model to apply a move to a game."""
    row: int = Field(..., ge=0, le=2, description="Row index 0..2.")
    col: int = Field(..., ge=0, le=2, description="Column index 0..2.")

    @model_validator(mode="after")
    def _validate_bounds(self) -> "MoveRequest":
        if not (0 <= self.row <= 2 and 0 <= self.col <= 2):
            raise ValueError("Row and col must be between 0 and 2.")
        return self


# PUBLIC_INTERFACE
class MoveResponse(BaseModel):
    """Response model after making a move."""
    game_id: str = Field(..., description="Game identifier.")
    board: List[List[str]] = Field(..., description="Board after the move.")
    next_player: Optional[Player] = Field(None, description="Next player to move (None if game ended).")
    status: GameStatus = Field(..., description="Updated game status.")
    winner: Optional[Player] = Field(default=None, description="Winner if any.")
    message: str = Field(..., description="Human-friendly status message.")


# PUBLIC_INTERFACE
class GameStatusResponse(BaseModel):
    """Response model for fetching current game status."""
    game_id: str = Field(..., description="Game identifier.")
    board: List[List[str]] = Field(..., description="Current board.")
    next_player: Optional[Player] = Field(None, description="Next player to move (None if finished).")
    status: GameStatus = Field(..., description="Current game status.")
    winner: Optional[Player] = Field(default=None, description="Winner if any.")
    available_moves: List[Tuple[int, int]] = Field(
        default_factory=list,
        description="List of available (row,col) moves when in progress."
    )


# PUBLIC_INTERFACE
class ErrorResponse(BaseModel):
    """Standard error envelope in Ocean Professional style."""
    error: str = Field(..., description="Error code or short label.")
    message: str = Field(..., description="Human-readable error description.")
    details: Optional[Dict[str, str]] = Field(default=None, description="Optional additional details.")
