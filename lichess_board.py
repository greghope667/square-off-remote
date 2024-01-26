import http.client
import json
import chess

from squareoff import SquareOff

# Local file for API key
import credentials

def request(endpoint, method="GET"):
	conn = http.client.HTTPSConnection("lichess.org")
	headers = {"Authorization":"Bearer "+credentials.LICHESS_BOARD_ACCESS_TOKEN}
	conn.request(method, endpoint, headers=headers)
	response = conn.getresponse()
	if response.status != 200:
		print(f"Error, call to {endpoint} failed with response:")
		print(response.status, response.reason)
		print(response.read(4096))
		raise RuntimeError("API call failed")
	return response

def stream(endpoint):
	response = request(endpoint)
	while True:
		event = response.readline().strip()
		if len(event) > 0:
			yield json.loads(event)

def find_game():
	print("Listening for game start event...")
	for event in stream("/api/stream/event"):
		if event["type"] == "gameStart":
			game = event["game"]
			print(f"Found game {game['gameId']}")
			if game["hasMoved"]:
				# Resuming existing games not yet implemented
				print(f"Warning: In-progress game {game['gameId']} ignored...")
			else:
				return game

def stream_game_state(gameId):
	for event in stream(f"/api/board/game/stream/{gameId}"):
		if event["type"] == "gameFull":
			yield event["state"]
		elif event["type"] == "gameState":
			yield event

def stream_game_moves(gameId):
	for state in stream_game_state(gameId):
		if state["status"] == "started":
			all_moves = state["moves"].split()
			if len(all_moves) > 0:
				yield chess.Move.from_uci(all_moves[-1])
		else:
			print(f"Game ended with status={state['status']}")
			return

def send_move(gameId, move):
	request(f"/api/board/game/{gameId}/move/{move}", method="POST")

def main():
	so = SquareOff()
	game_details = find_game()
	game_id = game_details["gameId"]
	board = chess.Board()

	move_stream = stream_game_moves(game_id)
	is_player_move = game_details["color"] == "white"

	player = so.start_game(player=chess.WHITE if is_player_move else chess.BLACK)

	try:
		while True:
			if is_player_move:
				move = player(board)
				send_move(game_id, move.uci())

			is_player_move ^= 1
			move = next(move_stream)
			so.make_move(move)
			board.push(move)

	except StopIteration:
		pass
	finally:
		so.end_game()
		so.disconnect()

if __name__=="__main__":
	main()





