from ai import find_best_move
from game_logic import check_win, is_board_full



# ============================================================
# VERIFICATION LIMIT
#
# None = verify all generated states
#
# Start with a small number first.
# ============================================================

MAX_STATES_TO_VERIFY = 4035944

# ============================================================
# REACHABLE STATE CACHE
# ============================================================

visited_generation_states = set()


# ============================================================
# GAME VALUES
#
# GREEN WIN =  1
# DRAW      =  0
# RED WIN   = -1
# ============================================================

GREEN_WIN = 1
DRAW = 0
RED_WIN = -1


# ============================================================
# ALL 10 WINNING LINES
# ============================================================

WIN_LINES = [

    # Rows
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (8, 9, 10, 11),
    (12, 13, 14, 15),

    # Columns
    (0, 4, 8, 12),
    (1, 5, 9, 13),
    (2, 6, 10, 14),
    (3, 7, 11, 15),

    # Diagonals
    (0, 5, 10, 15),
    (3, 6, 9, 12),
    
    
    (0, 1, 4, 5),
    (1, 2, 5, 6),
    (2, 3, 6, 7),




    (4, 5, 8, 9),
    (5, 6, 9, 10),
    (6, 7, 10, 11),




    (8, 9, 12, 13),
    (9, 10, 13, 14),
    (10, 11, 14, 15),

]


# ============================================================
# INDEPENDENT EXACT SOLVER
#
# GREEN maximizes
# RED minimizes
#
# Returns:
#
#   1  = GREEN can force win
#   0  = GREEN can force draw
#  -1  = RED can force win
# ============================================================

reference_cache = {}


def reference_value(board, is_green_turn):


    # --------------------------------------------------------
    # CACHE
    # --------------------------------------------------------

    key = (
        tuple(board),
        is_green_turn
    )

    if key in reference_cache:

        return reference_cache[key]


    # --------------------------------------------------------
    # TERMINAL STATES
    # --------------------------------------------------------

    if check_win(board, 2):

        return GREEN_WIN


    if check_win(board, 1):

        return RED_WIN


    if is_board_full(board):

        return DRAW


    # --------------------------------------------------------
    # GREEN TURN
    #
    # MAXIMIZE
    # --------------------------------------------------------

    if is_green_turn:


        best_value = RED_WIN


        for move in range(16):


            if board[move] == 0:


                board[move] = 2


                value = reference_value(
                    board,
                    False
                )


                board[move] = 0


                if value > best_value:

                    best_value = value


                # GREEN cannot do better than win

                if best_value == GREEN_WIN:

                    break


    # --------------------------------------------------------
    # RED TURN
    #
    # MINIMIZE
    # --------------------------------------------------------

    else:


        best_value = GREEN_WIN


        for move in range(16):


            if board[move] == 0:


                board[move] = 1


                value = reference_value(
                    board,
                    True
                )


                board[move] = 0


                if value < best_value:

                    best_value = value


                # RED cannot do better than win

                if best_value == RED_WIN:

                    break


    # --------------------------------------------------------
    # STORE
    # --------------------------------------------------------

    reference_cache[key] = best_value


    return best_value


# ============================================================
# GENERATE REACHABLE GREEN-TURN STATES
#
# RED always starts.
#
# We generate only legal game states that can actually occur
# in a real game.
# ============================================================

# ============================================================
# GENERATE REACHABLE GREEN-TURN STATES BY DEPTH
#
# RED always starts.
#
# The returned dictionary groups states by the number
# of occupied cells on the board.
# ============================================================

def generate_green_turn_states_by_depth():

    states_by_depth = {}

    board = [0] * 16


    def dfs(is_green_turn, depth):


        # ----------------------------------------------------
        # AVOID GENERATING THE SAME BOARD AGAIN
        # ----------------------------------------------------

        state_key = (
            tuple(board),
            is_green_turn
        )


        if state_key in visited_generation_states:

            return


        visited_generation_states.add(
            state_key
        )


        # ----------------------------------------------------
        # STOP AT TERMINAL STATES
        #
        # No moves are generated after someone wins.
        # ----------------------------------------------------

        if check_win(board, 1):

            return


        if check_win(board, 2):

            return


        if is_board_full(board):

            return


        # ----------------------------------------------------
        # GREEN TO MOVE
        #
        # Store this board under its current depth.
        # ----------------------------------------------------

        if is_green_turn:


            if depth not in states_by_depth:

                states_by_depth[depth] = []


            states_by_depth[depth].append(
                tuple(board)
            )


        # ----------------------------------------------------
        # DETERMINE CURRENT PLAYER
        # ----------------------------------------------------

        player = 2 if is_green_turn else 1


        # ----------------------------------------------------
        # GENERATE NEXT LEGAL MOVES
        # ----------------------------------------------------

        for move in range(16):


            if board[move] == 0:


                board[move] = player


                dfs(
                    not is_green_turn,
                    depth + 1
                )


                board[move] = 0


    # --------------------------------------------------------
    # RED ALWAYS STARTS
    # --------------------------------------------------------

    dfs(
        False,
        0
    )


    return states_by_depth



# ============================================================
# VERIFY OPTIMIZED AI
# ============================================================

# ============================================================
# VERIFY OPTIMIZED AI
# ============================================================

def verify_ai():


    print()
    print("========================================")
    print("GENERATING REACHABLE GREEN-TURN STATES")
    print("========================================")
    print()


    # ========================================================
    # GENERATE STATES GROUPED BY DEPTH
    # ========================================================

    states_by_depth = (
        generate_green_turn_states_by_depth()
    )


    # ========================================================
    # PRINT ACTUAL STATE DISTRIBUTION
    # ========================================================

    print()


    total_generated_states = 0


    for depth in sorted(states_by_depth):


        count = len(
            states_by_depth[depth]
        )


        total_generated_states += count


        print(
            "DEPTH",
            depth,
            ":",
            count,
            "states"
        )


    print()


    print(
        "TOTAL REACHABLE GREEN-TURN STATES:",
        total_generated_states
    )


    # ========================================================
    # BUILD DEPTH-BALANCED VERIFICATION SET
    #
    # MAX_STATES_TO_VERIFY means:
    #
    # maximum number of states selected from EACH depth.
    #
    # None means:
    #
    # verify ALL states.
    # ========================================================

    states_to_verify = []


    for depth in sorted(states_by_depth):


        depth_states = (
            states_by_depth[depth]
        )


        if MAX_STATES_TO_VERIFY is None:


            selected_states = depth_states


        else:


            selected_states = (
                depth_states[
                    :MAX_STATES_TO_VERIFY
                ]
            )


        states_to_verify.extend(
            selected_states
        )


    print()


    print(
        "TOTAL STATES SELECTED FOR VERIFICATION:",
        len(states_to_verify)
    )


    # ========================================================
    # START VERIFICATION
    # ========================================================

    print()
    print("========================================")
    print("STARTING VERIFICATION")
    print("========================================")
    print()


    verified = 0


    for state in states_to_verify:


        # ----------------------------------------------------
        # CONVERT IMMUTABLE TUPLE BACK TO LIST
        # ----------------------------------------------------

        board = list(state)


        # ----------------------------------------------------
        # TRUE GAME-THEORETIC VALUE
        #
        # GREEN is currently to move.
        # ----------------------------------------------------

        true_value = reference_value(
            board.copy(),
            True
        )


        # ----------------------------------------------------
        # OUR AI'S MOVE
        # ----------------------------------------------------

        ai_move = find_best_move(
            board.copy()
        )


        # ----------------------------------------------------
        # SAFETY CHECK
        #
        # AI must return a valid empty cell.
        # ----------------------------------------------------

        if (
            ai_move < 0
            or ai_move >= 16
            or board[ai_move] != 0
        ):


            print()
            print("========================================")
            print("VERIFICATION FAILED")
            print("========================================")

            print(
                "BOARD:",
                "".join(
                    map(str, board)
                )
            )

            print(
                "AI RETURNED INVALID MOVE:",
                ai_move
            )

            print("========================================")
            print()


            return False


        # ----------------------------------------------------
        # APPLY AI MOVE
        # ----------------------------------------------------

        board_after_ai_move = board.copy()

        board_after_ai_move[ai_move] = 2


        # ----------------------------------------------------
        # VALUE AFTER AI'S MOVE
        #
        # Now RED moves.
        # ----------------------------------------------------

        ai_move_value = reference_value(
            board_after_ai_move,
            False
        )


        # ----------------------------------------------------
        # VERIFY OPTIMALITY
        #
        # The value of the move selected by our AI
        # must equal the true optimal value.
        # ----------------------------------------------------

        if ai_move_value != true_value:


            print()
            print("========================================")
            print("VERIFICATION FAILED")
            print("========================================")

            print(
                "BOARD:",
                "".join(
                    map(str, board)
                )
            )

            print(
                "TRUE VALUE:",
                true_value
            )

            print(
                "AI MOVE:",
                ai_move
            )

            print(
                "AI MOVE VALUE:",
                ai_move_value
            )

            print(
                "AI CHOSE A SUBOPTIMAL MOVE"
            )

            print("========================================")
            print()


            return False


        # ----------------------------------------------------
        # STATE PASSED
        # ----------------------------------------------------

        verified += 1


        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        if verified % 1000 == 0:


            print(
                "VERIFIED:",
                verified,
                "/",
                len(states_to_verify)
            )


    # ========================================================
    # ALL STATES PASSED
    # ========================================================

    print()
    print("========================================")
    print("VERIFICATION PASSED")
    print("========================================")

    print(
        "ALL VERIFIED STATES:",
        verified
    )

    print(
        "NO SUBOPTIMAL GREEN MOVE FOUND"
    )

    print("========================================")
    print()


    return True
# ============================================================
# RUN VERIFIER
# ============================================================

if __name__ == "__main__":

    verify_ai()