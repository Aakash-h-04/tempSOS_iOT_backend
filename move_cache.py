import json
import os


# ============================================================
# CACHE FILE
# ============================================================

CACHE_FILE = "move_cache.json"


# ============================================================
# IN-MEMORY CACHE
# ============================================================

move_cache = {}


# ============================================================
# LOAD CACHE FROM DISK
# ============================================================

def load_move_cache():

    global move_cache


    # --------------------------------------------------------
    # CACHE FILE DOES NOT EXIST
    # --------------------------------------------------------

    if not os.path.exists(CACHE_FILE):

        move_cache = {}

        return


    # --------------------------------------------------------
    # LOAD JSON FILE
    # --------------------------------------------------------

    try:

        with open(
            CACHE_FILE,
            "r"
        ) as file:

            move_cache = json.load(
                file
            )


    except (
        json.JSONDecodeError,
        OSError
    ):

        # ----------------------------------------------------
        # If the file is corrupted or unreadable,
        # start with an empty cache.
        # ----------------------------------------------------

        move_cache = {}


# ============================================================
# SAVE CACHE TO DISK
# ============================================================

def save_move_cache():

    with open(
        CACHE_FILE,
        "w"
    ) as file:

        json.dump(
            move_cache,
            file
        )


# ============================================================
# GET CACHED MOVE
# ============================================================

def get_cached_move(board_string):

    return move_cache.get(
        board_string
    )


# ============================================================
# STORE MOVE
# ============================================================

def store_move(board_string, move):

    move_cache[board_string] = move

    save_move_cache()


# ============================================================
# CACHE SIZE
# ============================================================

def get_cache_size():

    return len(move_cache)