# Experimental stream of finished games from broadcasts to Square Off GKS 
# using Lichess API

import os
import io
import time

from simple_term_menu import TerminalMenu

import chess
import chess.pgn
import berserk

import player
from squareoff import SquareOff

# time in seconds between moves
sleeptime = 4

# Login to lichess.org, check all but user account select boxes and 
# create a personal token via https://lichess.org/account/oauth/token/create 
token = ""
session = berserk.TokenSession(token)
client = berserk.Client(session=session)

def main():
    bc_offical_list = [b for b in client.broadcasts.get_official(nb=20)]
    bc_menu_title = "Lichess Broadcasts"
    bc_menu_items = ["[" + b["tour"]["id"] + "] " + " -- " 
                             + b["tour"]["name"] + " -- " 
                             + b["tour"]["description"] 
                             for b in bc_offical_list] 
    bc_menu_exit = False
    bc_menu = TerminalMenu(
        title=bc_menu_title,
        menu_entries=bc_menu_items,
    )
    os.system("clear")
    while not bc_menu_exit:
        bc_sel = bc_menu.show()
        if bc_sel == None: 
            bc_menu_exit = True
        else: 
            rounds_menu_title = "Broadcast Rounds"
            rounds_list = [r for r in bc_offical_list[bc_sel]["rounds"]]
            rounds_menu_items = ["[" + r["id"] + "]" + " -- " + r["name"] + " -- " 
                                 + r["tour"]["description"] for r in rounds_list]
            rounds_menu_back = False
            rounds_menu = TerminalMenu(
                title=rounds_menu_title,
                menu_entries=rounds_menu_items,
            )
            while not rounds_menu_back:
                round_sel = rounds_menu.show()
                if round_sel == None: 
                    rounds_menu_back = True
                else: 
                    pgns = client.broadcasts.get_round_pgns(
                            broadcast_round_id=rounds_list[round_sel]["id"])
                    games_list = []
                    for g in pgns:
                        pgn = io.StringIO(g)
                        game = chess.pgn.read_game(pgn)
                        games_list.append(game)
                    games_menu_title = "Round Games"
                    games_menu_items = ["[" + g.headers["Event"] + " " 
                                        + g.headers["White"] + " vs " 
                                        + g.headers["Black"] + "]" + " -- " 
                                        + g.headers["Result"] for g in games_list]
                    games_menu_back = False
                    games_menu = TerminalMenu(
                        title=games_menu_title,
                        menu_entries=games_menu_items,
                    )   
                    while not games_menu_back:
                        game_sel = games_menu.show()
                        if game_sel == None:
                            games_menu_back = True
                        else: 
                            so = SquareOff()
                            try:
                                so.start_game()
                                board = chess.Board()

                                for move in games_list[game_sel].mainline_moves(): 
                                    print(move.uci())
                                    board.push(move)
                                    so.make_move(move)
                                    time.sleep(sleeptime)
                            finally:
                                so.disconnect()
                            games_menu_back = True
                    rounds_menu_back = False
            bc_menu_back = False

if __name__ == "__main__":
    main()
