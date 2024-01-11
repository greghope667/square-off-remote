# square-off-remote

This is my attempt at controlling a Grand Kingdom chess set from Square Off, directly from my PC instead of through the offical app.

## Working:
- Moves
- AI vs AI games
- Human vs AI games
- Voice control
- Lichess tournament (watch recent games)
- Play on Lichess (experimental, see below)

## Todo:
- Start position from FEN
- Reset board to initial position

### Lichess games howto:
- Login to Lichess and [create an access token](https://lichess.org/account/oauth/token/create?scopes[]=board:play&description=square-off-remote)
- Create the file `credentials.py` with the line `LICHESS_BOARD_ACCESS_TOKEN="lip_xxxxxx"`, with the token you generated
- Run `python lichess_board.py`, wait for the `Listening for game start` message
- Start a game on Lichess (I recommend playing versus stockfish for testing)

# License
GPL-3.0-or-later
