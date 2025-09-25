# Tic Tac Toe Backend (FastAPI)

A clean, modern API implementing Tic Tac Toe game logic with in-memory storage.

Run locally:
- Install: pip install -r requirements.txt
- Start: uvicorn tic_tac_toe_backend.src.api.main:app --host 0.0.0.0 --port 8000 --reload
- Docs: http://localhost:8000/docs

Endpoints:
- POST /api/v1/tictactoe/games -> create a new game
- GET  /api/v1/tictactoe/games/{game_id} -> current game status
- POST /api/v1/tictactoe/games/{game_id}/moves -> make a move (body: {"row": 0, "col": 0})

Notes:
- Game state is kept in-memory and resets on server restart.
- Ocean Professional style reflected in API docs and response shapes.
