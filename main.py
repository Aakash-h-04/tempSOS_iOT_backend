from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import (PlainTextResponse,FileResponse)

from fastapi.staticfiles import StaticFiles

from game_logic import *
from ai import *
from move_cache import *


import time

# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(
        directory="static"
    ),
    name="static"
)

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "*"
    ],

    allow_credentials=False,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ]
)

# ========================================================
# LOAD PERSISTENT MOVE CACHE
# ========================================================

load_move_cache()

print(
    "PERSISTENT MOVE CACHE LOADED:",
    get_cache_size(),
    "positions"
)


# ============================================================
# HOME ENDPOINT
# ============================================================

@app.get("/")
def home():

    return FileResponse(
        "static/index.html"
    )


# ============================================================
# HEALTH CHECK ENDPOINT
# ============================================================

@app.get("/health")
def health():

    return PlainTextResponse(
        "abi tk toh changaa-siiii"
    )




def solve_board(
    board_string: str
):

    board_string = board_string.strip()


    # ========================================================
    # VALIDATE LENGTH
    # ========================================================

    if len(board_string) != 16:

        return (
            "INVALID BOARD: Board must contain exactly 16 cells",
            400
        )


    # ========================================================
    # VALIDATE CELL VALUES
    # ========================================================

    for cell in board_string:

        if cell not in "012":

            return (
                "INVALID BOARD: Cells must contain only 0, 1 or 2",
                400
            )


    # ========================================================
    # CONVERT STRING → BOARD
    # ========================================================

    board = [
        int(cell)
        for cell in board_string
    ]


    # ========================================================
    # CHECK GAME OVER
    # ========================================================

    if check_win(board, 1):

        return (
            "GAME OVER: RED has already won",
            400
        )


    if check_win(board, 2):

        return (
            "GAME OVER: GREEN has already won",
            400
        )


    if is_board_full(board):

        return (
            "GAME OVER: DRAW",
            400
        )


    # ========================================================
    # VALIDATE GREEN'S TURN
    # ========================================================

    red_count = board.count(1)

    green_count = board.count(2)


    if red_count != green_count + 1:

        return (
            "INVALID BOARD: GREEN is not the player to move",
            400
        )


    # ========================================================
    # CHECK CACHE
    # ========================================================

    cached_move = get_cached_move(
        board_string
    )


    if cached_move is not None:

        return (
            str(cached_move),
            200
        )


    # ========================================================
    # CACHE MISS → AI
    # ========================================================

    best_move = find_best_move(
        board
    )


    store_move(
        board_string,
        best_move
    )


    return (
        str(best_move),
        200
    )
# ============================================================
# BEST MOVE ENDPOINT
# ============================================================

'''
@app.post(
    "/best-move",
    response_class=PlainTextResponse
)
async def best_move(request: Request):


    # ========================================================
    # READ RAW REQUEST BODY
    # ========================================================

    board_state = await request.body()

    board_string = board_state.decode().strip()


    # Print received board
    print("Received board:", board_string)


    # ========================================================
    # VALIDATE LENGTH
    #
    # Board must contain exactly 16 cells
    # ========================================================

    if len(board_string) != 16:

        return PlainTextResponse(
            "INVALID BOARD: Board must contain exactly 16 cells",
            status_code=400
        )


    # ========================================================
    # VALIDATE CELL VALUES
    #
    # Allowed:
    #
    # 0 = EMPTY
    # 1 = RED
    # 2 = GREEN
    # ========================================================

    for cell in board_string:

        if cell not in "012":

            return PlainTextResponse(
                "INVALID BOARD: Cells must contain only 0, 1 or 2",
                status_code=400
            )


    # ========================================================
    # CONVERT STRING → INTEGER BOARD
    # ========================================================

    board = [int(cell) for cell in board_string]

    print("Validated board:", board)


    # ========================================================
    # VALIDATE GAME IS NOT ALREADY FINISHED
    #
    # IMPORTANT:
    #
    # This must happen BEFORE turn validation.
    #
    # A board where GREEN already won will normally have:
    #
    # RED count = GREEN count
    #
    # because GREEN made the last move.
    # ========================================================

    if check_win(board, 1):

        return PlainTextResponse(
            "GAME OVER: RED has already won",
            status_code=400
        )


    if check_win(board, 2):

        return PlainTextResponse(
            "GAME OVER: GREEN has already won",
            status_code=400
        )
        
    # ========================================================
    # VALIDATE DRAW
    #
    # If board is full and nobody has won,
    # the game has ended in a draw.
    # ========================================================

    if is_board_full(board):

        return PlainTextResponse(
            "GAME OVER: DRAW",
            status_code=400
        )


    # ========================================================
    # VALIDATE TURN
    #
    # RED always starts.
    #
    # This API is called only when GREEN must move.
    #
    # Therefore:
    #
    # RED count = GREEN count + 1
    # ========================================================

    red_count = board.count(1)

    green_count = board.count(2)


    if red_count != green_count + 1:

        return PlainTextResponse(
            "INVALID BOARD: GREEN is not the player to move",
            status_code=400
        )


    # # ========================================================
    # # TEST AI MODULE
    # # ========================================================



    # ========================================================
    # BENCHMARK START
    # ========================================================

    start_time = time.perf_counter()


    # ========================================================
    # CHECK PERSISTENT MOVE CACHE
    # ========================================================

    cached_move = get_cached_move(
        board_string
    )
    
    cache_status = "MISS"


    # ========================================================
    # CACHE HIT
    # ========================================================

    if cached_move is not None:

        cache_status = "HIT"

        print(
            "CACHE HIT:",
            cached_move
        )


        best_move = cached_move


    # ========================================================
    # CACHE MISS
    # ========================================================

    else:


        print(
            "CACHE MISS - SOLVING WITH AI"
        )


        # ----------------------------------------------------
        # FIND BEST GREEN MOVE
        # ----------------------------------------------------

        best_move = find_best_move(
            board
        )


        # ----------------------------------------------------
        # STORE RESULT IN PERSISTENT CACHE
        # ----------------------------------------------------

        store_move(
            board_string,
            best_move
        )


    # ========================================================
    # BENCHMARK END
    # ========================================================

    end_time = time.perf_counter()


    # ========================================================
    # CALCULATE EXECUTION TIME
    # ========================================================

    execution_time = (
        end_time - start_time
    )


    execution_time_ms = (
        execution_time * 1000
    )


    # ========================================================
    # GET AI STATISTICS
    # ========================================================

    if cache_status == "HIT":


        statistics = {
            "nodes_visited": 0,
            "alpha_beta_cutoffs": 0,
            "transposition_hits": 0,
            "transposition_table_size": 0
        }


    else:


        statistics = get_statistics()


    # ========================================================
    # PRINT SOLVER RESULT
    # ========================================================

    print()
    print("========================================")
    print("GREEN AI SOLVER BENCHMARK")
    print("========================================")

    print("BEST MOVE:", best_move)
    
    print(
        "CACHE STATUS:",
        cache_status
    )

    print(
        "EXECUTION TIME:",
        execution_time_ms,
        "ms"
    )

    print(
        "NODES VISITED:",
        statistics["nodes_visited"]
    )

    print(
        "ALPHA-BETA CUTOFFS:",
        statistics["alpha_beta_cutoffs"]
    )

    print(
        "TRANSPOSITION HITS:",
        statistics["transposition_hits"]
    )

    print(
        "TRANSPOSITION TABLE SIZE:",
        statistics["transposition_table_size"]
    )

    print("========================================")
    print()


    # ========================================================
    # RETURN BEST MOVE
    # ========================================================

    return str(
        best_move
    )
'''

@app.post(
    "/best-move",
    response_class=PlainTextResponse
)
async def best_move(
    request: Request
):


    # ========================================================
    # READ RAW REQUEST BODY
    # ========================================================

    board_state = await request.body()

    board_string = (
        board_state
        .decode()
        .strip()
    )


    # ========================================================
    # USE SHARED LOGIC
    # ========================================================

    result, status_code = solve_board(
        board_string
    )


    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return PlainTextResponse(
        result,
        status_code=status_code
    )

@app.get(
    "/best-move",
    response_class=PlainTextResponse
)
def get_best_move(
    board: str = Query(...)
):


    result, status_code = solve_board(
        board
    )


    return PlainTextResponse(
        result,
        status_code=status_code
    )
