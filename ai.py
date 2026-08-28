# ============================================================
# AI ENGINE
# ============================================================



from game_logic import check_win, is_board_full


# ============================================================
# SOLVER STATISTICS
# ============================================================

nodes_visited = 0

alpha_beta_cutoffs = 0

transposition_hits = 0

# ============================================================
# TRANSPOSITION TABLE
#
# Each entry stores:
#
# score
# entry type
#
# Entry types:
#
# EXACT = exact minimax value
# LOWER = lower bound
# UPPER = upper bound
# ============================================================

transposition_table = {}


EXACT = 0
LOWER = 1
UPPER = 2

# ============================================================
# TRANSPOSITION TABLE
#
# Stores already evaluated game positions.
# ============================================================

transposition_table = {}

# ============================================================
# POSITIONAL MOVE ORDER
#
# Search stronger central positions first.
# This improves Alpha-Beta pruning.
# ============================================================




# ============================================================
# MOVE ORDER
#
# Strategically stronger positions are searched first.
#
# This improves alpha-beta pruning efficiency.
# ============================================================

MOVE_ORDER = [

    # Center

    5,
    6,
    9,
    10,


    # Near-center edges

    1,
    2,
    4,
    7,
    8,
    11,
    13,
    14,


    # Corners

    0,
    3,
    12,
    15

]


POSITION_ORDER = [

    # ========================================================
    # CENTRAL 2 x 2
    # ========================================================

    5, 6, 9, 10,


    # ========================================================
    # CORNERS
    # ========================================================

    0, 3, 12, 15,


    # ========================================================
    # REMAINING CELLS
    # ========================================================

    1, 2, 4, 7,
    8, 11, 13, 14
]

# ============================================================
# GET ALL EMPTY CELLS
# ============================================================

def get_empty_cells(board):

    empty_cells = []


    for i in range(16):

        if board[i] == 0:

            empty_cells.append(i)


    return empty_cells


# ============================================================
# GET ORDERED EMPTY CELLS
#
# Returns only empty cells,
# but in positional search priority order.
# ============================================================

def get_ordered_empty_cells(board):

    ordered_moves = []


    for move in POSITION_ORDER:

        if board[move] == 0:

            ordered_moves.append(move)


    return ordered_moves

# ============================================================
# EVALUATE BOARD
#
# GREEN / COMPUTER = 2
# RED / USER      = 1
# ============================================================



# ============================================================
# GET TACTICALLY ORDERED MOVES
#
# Priority:
#
# 1. Immediate winning moves
# 2. Immediate blocking moves
# 3. Positional priority
#
# All legal moves are still included.
# ============================================================

# ============================================================
# GET TACTICAL MOVE GROUPS
#
# Returns:
#
# 1. Immediate winning moves
# 2. Immediate blocking moves
# 3. Remaining moves
#
# All moves remain legal moves.
# ============================================================

def get_tactical_move_groups(board, player):


    # --------------------------------------------------------
    # NORMAL POSITIONAL ORDER
    # --------------------------------------------------------

    normal_moves = get_ordered_empty_cells(board)


    winning_moves = []

    blocking_moves = []

    remaining_moves = []


    # --------------------------------------------------------
    # FIND IMMEDIATE WINNING MOVES
    # --------------------------------------------------------

    for move in normal_moves:

        board[move] = player


        if check_win(board, player):

            winning_moves.append(move)


        board[move] = 0


    # --------------------------------------------------------
    # FIND OPPONENT IMMEDIATE WINNING MOVES
    # --------------------------------------------------------

    opponent = 1 if player == 2 else 2


    for move in normal_moves:

        board[move] = opponent


        if check_win(board, opponent):

            blocking_moves.append(move)


        board[move] = 0


    # --------------------------------------------------------
    # REMAINING MOVES
    # --------------------------------------------------------

    for move in normal_moves:

        if (
            move not in winning_moves
            and move not in blocking_moves
        ):

            remaining_moves.append(move)


    # --------------------------------------------------------
    # RETURN GROUPS
    # --------------------------------------------------------

    return (
        winning_moves,
        blocking_moves,
        remaining_moves
    )
    

def evaluate_board(board):


    # GREEN wins

    if check_win(board, 2):

        return 1


    # RED wins

    if check_win(board, 1):

        return -1


    # DRAW / GAME NOT FINISHED

    return 0

# ============================================================
# MINIMAX WITH ALPHA-BETA PRUNING
# ============================================================




# ============================================================
# CREATE UNIQUE BOARD KEY
#
# The same board must have different keys depending on
# whose turn it is.
# ============================================================



# ============================================================
# BOARD SYMMETRY HELPERS
#
# A square board has 8 geometric symmetries:
#
# 4 rotations
# 4 reflections
# ============================================================


def rotate_90(board):

    return [
        board[12], board[8], board[4], board[0],
        board[13], board[9], board[5], board[1],
        board[14], board[10], board[6], board[2],
        board[15], board[11], board[7], board[3]
    ]


def rotate_180(board):

    return [
        board[15], board[14], board[13], board[12],
        board[11], board[10], board[9], board[8],
        board[7], board[6], board[5], board[4],
        board[3], board[2], board[1], board[0]
    ]


def rotate_270(board):

    return [
        board[3], board[7], board[11], board[15],
        board[2], board[6], board[10], board[14],
        board[1], board[5], board[9], board[13],
        board[0], board[4], board[8], board[12]
    ]


def reflect_horizontal(board):

    return [
        board[12], board[13], board[14], board[15],
        board[8], board[9], board[10], board[11],
        board[4], board[5], board[6], board[7],
        board[0], board[1], board[2], board[3]
    ]
    
    
# ============================================================
# GET CANONICAL BOARD
#
# Generate all 8 symmetries and choose the smallest
# lexicographic representation.
# ============================================================

def get_canonical_board(board):


    # --------------------------------------------------------
    # ORIGINAL
    # --------------------------------------------------------

    b0 = tuple(board)


    # --------------------------------------------------------
    # ROTATIONS
    # --------------------------------------------------------

    b90 = tuple(
        rotate_90(b0)
    )


    b180 = tuple(
        rotate_180(b0)
    )


    b270 = tuple(
        rotate_270(b0)
    )


    # --------------------------------------------------------
    # REFLECTIONS
    #
    # Reflect original and its rotations.
    # --------------------------------------------------------

    r0 = tuple(
        reflect_horizontal(b0)
    )


    r90 = tuple(
        reflect_horizontal(b90)
    )


    r180 = tuple(
        reflect_horizontal(b180)
    )


    r270 = tuple(
        reflect_horizontal(b270)
    )


    # --------------------------------------------------------
    # RETURN CANONICAL REPRESENTATION
    # --------------------------------------------------------

    return min(
        b0,
        b90,
        b180,
        b270,
        r0,
        r90,
        r180,
        r270
    )

# ============================================================
# CREATE SYMMETRY-AWARE BOARD KEY
# ============================================================

def get_board_key(board, is_green_turn):


    canonical_board = get_canonical_board(
        board
    )


    return (
        canonical_board,
        is_green_turn
    )



# ============================================================
# MINIMAX WITH
#
# ALPHA-BETA PRUNING
# +
# TRANSPOSITION TABLE
# ============================================================

def minimax(
    board,
    is_green_turn,
    alpha,
    beta,
    depth
):


    global nodes_visited
    global alpha_beta_cutoffs
    global transposition_hits


    # Count this recursive state

    nodes_visited += 1

    # ========================================================
    # TERMINAL STATES
    # ========================================================

    # GREEN WINS
    #
    # Faster GREEN win is better.

    if check_win(board, 2):

        return 100000 - depth


    # --------------------------------------------------------

    # RED WINS
    #
    # Slower RED win is better for GREEN.

    if check_win(board, 1):

        return -100000 + depth


    # --------------------------------------------------------

    # DRAW

    if is_board_full(board):

        return 0


    # ========================================================
    # SAVE ORIGINAL ALPHA AND BETA
    #
    # Needed to correctly determine whether the final score
    # is EXACT, LOWER BOUND or UPPER BOUND.
    # ========================================================

    alpha_original = alpha

    beta_original = beta


    # ========================================================
    # CREATE TRANSPOSITION KEY
    # ========================================================

    board_key = get_board_key(
        board,
        is_green_turn
    )


    # ========================================================
    # TRANSPOSITION TABLE LOOKUP
    # ========================================================

    if board_key in transposition_table:
        
        transposition_hits += 1

        cached_score, entry_type = (
            transposition_table[board_key]
        )


        # ----------------------------------------------------
        # EXACT VALUE
        # ----------------------------------------------------

        if entry_type == EXACT:

            return cached_score


        # ----------------------------------------------------
        # LOWER BOUND
        # ----------------------------------------------------

        elif entry_type == LOWER:

            if cached_score > alpha:

                alpha = cached_score


        # ----------------------------------------------------
        # UPPER BOUND
        # ----------------------------------------------------

        elif entry_type == UPPER:

            if cached_score < beta:

                beta = cached_score


        # ----------------------------------------------------
        # CACHE CAUSED CUTOFF
        # ----------------------------------------------------

        if alpha >= beta:

            return cached_score


    # ========================================================
    # GREEN TURN
    #
    # MAXIMIZE
    # ========================================================

    if is_green_turn:


        best_score = -1000000


        # Tactical move ordering

        winning_moves, blocking_moves, remaining_moves = (
            get_tactical_move_groups(
                board,
                2
            )
        )
        # ========================================================
        # IMMEDIATE GREEN WIN
        #
        # Since winning moves are already calculated,
        # no additional check_win() is required.
        # ========================================================

        if winning_moves:

            return 100000 - (depth + 1)
        

        ordered_moves = (
            winning_moves
            + blocking_moves
            + remaining_moves
        )



        # ----------------------------------------------------
        # TRY ALL MOVES
        # ----------------------------------------------------

        for move in ordered_moves:


            # Make GREEN move

            board[move] = 2


            # ========================================================
            # IMMEDIATE GREEN WIN
            # ========================================================

            


            # ========================================================
            # OTHERWISE SEARCH RED RESPONSE
            # ========================================================



            score = minimax(
                board,
                False,
                alpha,
                beta,
                depth + 1
            )


            # Undo move

            board[move] = 0


            # Keep best score

            if score > best_score:

                best_score = score


            # Update alpha

            if best_score > alpha:

                alpha = best_score


            # Alpha-Beta cutoff

            if alpha >= beta:

                alpha_beta_cutoffs += 1
                break


    # ========================================================
    # RED TURN
    #
    # MINIMIZE
    # ========================================================

    else:


        best_score = 1000000


        # Tactical move ordering

        winning_moves, blocking_moves, remaining_moves = (
            get_tactical_move_groups(
                board,
                1
            )
        )
        
        # ========================================================
        # IMMEDIATE RED WIN
        # ========================================================

        if winning_moves:

            return -100000 + (depth + 1)
        
        ordered_moves = (
            winning_moves
            + blocking_moves
            + remaining_moves
        )


        # ----------------------------------------------------
        # TRY ALL MOVES
        # ----------------------------------------------------

        for move in ordered_moves:


            # Make RED move

            board[move] = 1


            

            



            score = minimax(
                board,
                True,
                alpha,
                beta,
                depth + 1
            )


            # Undo move

            board[move] = 0


            # Keep worst score for GREEN

            if score < best_score:

                best_score = score


            # Update beta

            if best_score < beta:

                beta = best_score


            # Alpha-Beta cutoff

            if alpha >= beta:

                alpha_beta_cutoffs += 1
                break


    # ========================================================
    # DETERMINE CACHE ENTRY TYPE
    # ========================================================

    if best_score <= alpha_original:

        entry_type = UPPER


    elif best_score >= beta_original:

        entry_type = LOWER


    else:

        entry_type = EXACT


    # ========================================================
    # STORE IN TRANSPOSITION TABLE
    # ========================================================

    transposition_table[board_key] = (
        best_score,
        entry_type
    )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return best_score

# ============================================================
# FIND BEST MOVE FOR GREEN
# ============================================================

def find_best_move(board):
    clear_transposition_table()
    
    reset_statistics()

    # Best score found so far

    best_score = -1000000


    # Best move found so far

    best_move = -1


    # Get moves in good search order

    # ordered_moves = get_ordered_empty_cells(board)
    
    winning_moves, blocking_moves, remaining_moves = (
        get_tactical_move_groups(
            board,
            2
        )
    )

    # ========================================================
    # IMMEDIATE GREEN WIN
    #
    # Winning moves were already detected during tactical
    # analysis, so return the highest-priority one directly.
    # ========================================================

    if winning_moves:

        return winning_moves[0]


    ordered_moves = (
        blocking_moves
        + remaining_moves
    )
    
    # ========================================================
    # TRY EVERY POSSIBLE GREEN MOVE
    # ========================================================

    for move in ordered_moves:


        # Simulate GREEN move

        board[move] = 2


        # ========================================================
        # OTHERWISE EVALUATE THE POSITION
        # ========================================================

        score = minimax(
            board,
            False,
            -1000000,
            1000000,
            1
        )


        # Undo simulated GREEN move

        board[move] = 0


        # ----------------------------------------------------
        # Keep strictly better move
        #
        # This means if two moves have exactly the same score,
        # the first one in our move ordering is retained.
        # ----------------------------------------------------

        if score > best_score:

            best_score = score

            best_move = move


    # ========================================================
    # RETURN BEST MOVE
    # ========================================================

    return best_move


# ============================================================
# CLEAR AI CACHE
# ============================================================

def clear_transposition_table():

    transposition_table.clear()
    
    
    
   
   
   
# ============================================================
# GET SOLVER STATISTICS
# ============================================================

def get_statistics():

    return {

        "nodes_visited": nodes_visited,

        "alpha_beta_cutoffs": alpha_beta_cutoffs,

        "transposition_hits": transposition_hits,

        "transposition_table_size":
            len(transposition_table)
    } 
    
    
# ============================================================
# RESET SOLVER STATISTICS
# ============================================================

def reset_statistics():

    global nodes_visited
    global alpha_beta_cutoffs
    global transposition_hits


    nodes_visited = 0

    alpha_beta_cutoffs = 0

    transposition_hits = 0