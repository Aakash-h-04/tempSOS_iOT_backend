console.log(
    "SCRIPT LOADED AT:",
    new Date().toISOString()
);

window.addEventListener(
    "beforeunload",
    () => {

        console.warn(
            "PAGE IS UNLOADING / RELOADING"
        );

    }
);


window.addEventListener(
    "error",
    event => {

        console.error(
            "JAVASCRIPT ERROR:",
            event.error
        );

    }
);


// ============================================================
// GET HTML ELEMENTS
// ============================================================

const boardElement = document.getElementById(
    "board"
);

const resultElement = document.getElementById(
    "result"
);

const newGameButton = document.getElementById(
    "newGameButton"
);


// ============================================================
// GAME STATE
//
// 0 = EMPTY
// 1 = RED
// 2 = GREEN
// ============================================================

const board = Array(16).fill(0);

let gameOver = false;

let aiThinking = false;

let gameVersion = 0;


// ============================================================
// WINNING 2 x 2 SQUARES
//
// The game is won by occupying all four cells
// of any complete 2 x 2 square.
// ============================================================




// ============================================================
// WINNING COMBINATIONS
//
// 4 × 4 TIC-TAC-TOE
//
// A player wins by occupying:
//
// 1. Any complete row
// 2. Any complete column
// 3. Either main diagonal
// ============================================================

const winningCombinations = [

    // --------------------------------------------------------
    // TOP ROW OF 2 × 2 SQUARES
    // --------------------------------------------------------

    [0, 1, 4, 5],
    [1, 2, 5, 6],
    [2, 3, 6, 7],


    // --------------------------------------------------------
    // MIDDLE ROW OF 2 × 2 SQUARES
    // --------------------------------------------------------

    [4, 5, 8, 9],
    [5, 6, 9, 10],
    [6, 7, 10, 11],


    // --------------------------------------------------------
    // BOTTOM ROW OF 2 × 2 SQUARES
    // --------------------------------------------------------

    [8, 9, 12, 13],
    [9, 10, 13, 14],
    [10, 11, 14, 15],


    [0, 1, 2, 3], 
    [4, 5, 6, 7], 
    [8, 9, 10, 11],
    [12, 13, 14, 15],

    [0, 4, 8, 12], 
    [1, 5, 9, 13],
    [2, 6, 10, 14],
    [3, 7, 11, 15], 

    [0, 5, 10, 15],
    [3, 6, 9, 12]

];


// ============================================================
// CREATE BOARD
// ============================================================

for (let i = 0; i < 16; i++) {

    const cell = document.createElement(
        "button"
    );

    cell.type = "button";


    // --------------------------------------------------------
    // CELL CLASS
    // --------------------------------------------------------

    cell.classList.add(
        "cell"
    );


    // --------------------------------------------------------
    // STORE BOARD INDEX
    // --------------------------------------------------------

    cell.dataset.index = i;


    // --------------------------------------------------------
    // CLICK EVENT
    // --------------------------------------------------------

    cell.addEventListener(
        "click",
        () => {

            handleHumanMove(
                i
            );

        }
    );


    // --------------------------------------------------------
    // ADD TO BOARD
    // --------------------------------------------------------

    boardElement.appendChild(
        cell
    );

}


// ============================================================
// HANDLE HUMAN MOVE
//
// Human = RED
// ============================================================

function handleHumanMove(index) {


    // --------------------------------------------------------
    // DO NOT ALLOW MOVE IF:
    //
    // 1. Game is over
    // 2. AI is thinking
    // 3. Cell is occupied
    // --------------------------------------------------------

    if (gameOver) {

        return;

    }


    if (aiThinking) {

        return;

    }


    if (board[index] !== 0) {

        return;

    }


    // --------------------------------------------------------
    // HUMAN PLAYS RED
    // --------------------------------------------------------

    board[index] = 1;


    updateCell(
        index
    );

    showStatus(
        "🟢 GREEN AI is thinking..."
    );


    // --------------------------------------------------------
    // CHECK GAME OVER
    // --------------------------------------------------------

    if (checkGameOver()) {

        return;

    }


    // --------------------------------------------------------
    // REQUEST AI MOVE
    // --------------------------------------------------------

    requestAIMove();

}


// ============================================================
// UPDATE CELL
// ============================================================

function updateCell(index) {


    const cell = document.querySelector(
        `.cell[data-index="${index}"]`
    );


    const value = board[index];


    // --------------------------------------------------------
    // DISPLAY VALUE
    // --------------------------------------------------------

    // --------------------------------------------------------
    // DISPLAY PLAYER SYMBOL
    // --------------------------------------------------------

    if (value === 0) {

        cell.textContent = "";

    }


    else if (value === 1) {

        cell.textContent = "❌";

    }


    else {

        cell.textContent = "🟢";

    }


    // --------------------------------------------------------
    // REMOVE OLD CLASSES
    // --------------------------------------------------------

    cell.classList.remove(
        "empty",
        "red",
        "green",
        "ai-move"
    );


    // --------------------------------------------------------
    // ADD NEW CLASS
    // --------------------------------------------------------

    if (value === 0) {

        cell.classList.add(
            "empty"
        );

    }


    else if (value === 1) {

        cell.classList.add(
            "red"
        );

    }


    else {

        cell.classList.add(
            "green"
        );

    }

}


// ============================================================
// INITIALIZE BOARD DISPLAY
// ============================================================

for (let i = 0; i < 16; i++) {

    updateCell(
        i
    );

}


// ============================================================
// REQUEST GREEN AI MOVE
// ============================================================

async function requestAIMove() {


    // --------------------------------------------------------
    // PREVENT MULTIPLE AI REQUESTS
    // --------------------------------------------------------

    if (aiThinking) {

        return;

    }


    aiThinking = true;


    const currentGameVersion = gameVersion;


    // --------------------------------------------------------
    // DISABLE BOARD
    // --------------------------------------------------------

    setBoardDisabled(
        true
    );


    // --------------------------------------------------------
    // CONVERT BOARD TO STRING
    // --------------------------------------------------------

    const boardString = board.join(
        ""
    );


    // --------------------------------------------------------
    // SHOW THINKING MESSAGE
    // --------------------------------------------------------

    showStatus(
        "🟢 GREEN AI is thinking..."
    );


    try {


        // ----------------------------------------------------
        // SEND BOARD TO BACKEND
        // ----------------------------------------------------

        const response = await fetch(
            "/best-move",
            {

                method: "POST",

                headers: {

                    "Content-Type": "text/plain"

                },

                body: boardString

            }
        );


        // ----------------------------------------------------
        // READ RESPONSE
        // ----------------------------------------------------

        const responseText = await response.text();


        // ----------------------------------------------------
        // IGNORE RESPONSE FROM AN OLD GAME
        // ----------------------------------------------------

        if (currentGameVersion !== gameVersion) {

            return;

        }


        // ----------------------------------------------------
        // HANDLE BACKEND ERROR
        // ----------------------------------------------------

        if (!response.ok) {


            showStatus(
                responseText
            );


            console.error(
                "BACKEND ERROR:",
                responseText
            );


            return;

        }


        // ----------------------------------------------------
        // CONVERT RESPONSE TO MOVE
        // ----------------------------------------------------

        const bestMove = parseInt(
            responseText.trim(),
            10
        );


        // ----------------------------------------------------
        // VALIDATE AI MOVE
        // ----------------------------------------------------

        if (

            Number.isNaN(bestMove) ||

            bestMove < 0 ||

            bestMove >= 16 ||

            board[bestMove] !== 0

        ) {


            throw new Error(
                "Backend returned an invalid move: " +
                responseText
            );

        }


        // ----------------------------------------------------
        // APPLY GREEN MOVE
        // ----------------------------------------------------

        board[bestMove] = 2;


        // ----------------------------------------------------
        // UPDATE CELL
        // ----------------------------------------------------

        updateCell(
            bestMove
        );


        // ----------------------------------------------------
        // HIGHLIGHT AI MOVE
        // ----------------------------------------------------

        const bestMoveCell = document.querySelector(
            `.cell[data-index="${bestMove}"]`
        );


        bestMoveCell.classList.add(
            "ai-move"
        );


        // ----------------------------------------------------
        // CHECK GAME OVER
        //
        // IMPORTANT:
        // This checks:
        //
        // 1. RED win
        // 2. GREEN win
        // 3. DRAW
        //
        // If the game ended,
        // immediately stop here.
        // ----------------------------------------------------

        if (checkGameOver()) {

            return;

        }


        // ----------------------------------------------------
        // GAME CONTINUES
        // ----------------------------------------------------

        showStatus(
            "❌ Your turn"
        );

    }


    catch (error) {


        console.error(
            "AI REQUEST ERROR:",
            error
        );


        showStatus(
            "ERROR: Could not get GREEN AI move."
        );

    }


    finally {


        // ----------------------------------------------------
        // AI FINISHED
        // ----------------------------------------------------

        aiThinking = false;


        // ----------------------------------------------------
        // ENABLE BOARD ONLY IF GAME CONTINUES
        // ----------------------------------------------------

        if (!gameOver) {

            setBoardDisabled(
                false
            );

        }

    }

}

// ============================================================
// CHECK WIN
// ============================================================

// ============================================================
// CHECK WIN
//
// Returns:
//
// null
//      → no win
//
// winning combination
//      → win found
// ============================================================

function checkWin(player) {


    for (
        const combination of winningCombinations
    ) {


        const isWinner =
            combination.every(
                index =>
                    board[index] === player
            );


        if (isWinner) {

            return combination;

        }

    }


    return null;

}

// ============================================================
// HIGHLIGHT WINNING CELLS
// ============================================================

function highlightWinningCells(
    winningCells
) {


    for (
        const index of winningCells
    ) {


        const cell = document.querySelector(
            `.cell[data-index="${index}"]`
        );


        cell.classList.add(
            "winning-cell"
        );

    }

}


// ============================================================
// CHECK BOARD FULL
// ============================================================

function isBoardFull() {

    return !board.includes(
        0
    );

}


// ============================================================
// CHECK GAME OVER
// ============================================================

// ============================================================
// CHECK GAME OVER
// ============================================================
function checkGameOver() {


    // ========================================================
    // CHECK RED WIN
    // ========================================================

    const redWinningCells = checkWin(
        1
    );


    if (redWinningCells) {


        gameOver = true;

        resultElement.classList.add(
            "game-ended"
        );


        highlightWinningCells(
            redWinningCells
        );


        showStatus(
            "❌ YOU WIN!"
        );


        setBoardDisabled(
            true
        );


        return true;

    }


    // ========================================================
    // CHECK GREEN WIN
    // ========================================================

    const greenWinningCells = checkWin(
        2
    );


    if (greenWinningCells) {


        gameOver = true;

        resultElement.classList.add(
            "game-ended"
        );


        highlightWinningCells(
            greenWinningCells
        );


        showStatus(
            "🟢 GREEN AI WINS!"
        );


        setBoardDisabled(
            true
        );


        return true;

    }


    // ========================================================
    // CHECK DRAW
    //
    // ONLY AFTER CHECKING BOTH PLAYERS' WINS
    // ========================================================

    const isDraw = board.every(
        value => value !== 0
    );


    if (isDraw) {


        gameOver = true;

        resultElement.classList.add(
            "game-ended"
        );



        showStatus(
            "🤝 DRAW!"
        );


        setBoardDisabled(
            true
        );


        return true;

    }


    // ========================================================
    // GAME CONTINUES
    // ========================================================

    return false;

}


// ============================================================
// ENABLE / DISABLE BOARD
// ============================================================

function setBoardDisabled(disabled) {


    const cells = document.querySelectorAll(
        ".cell"
    );


    for (const cell of cells) {


        cell.style.pointerEvents =
            disabled
                ? "none"
                : "auto";


        if (disabled) {

            cell.classList.add(
                "disabled"
            );

        }
        else {

            cell.classList.remove(
                "disabled"
            );

        }

    }

}



// ============================================================
// START NEW GAME
// ============================================================

function startNewGame() {

    resultElement.classList.remove(
        "game-ended"
    );

    gameVersion++;


    // --------------------------------------------------------
    // RESET BOARD DATA
    // --------------------------------------------------------

    for (let i = 0; i < 16; i++) {

        board[i] = 0;

    }


    // --------------------------------------------------------
    // RESET GAME STATE
    // --------------------------------------------------------

    gameOver = false;

    aiThinking = false;


    // --------------------------------------------------------
    // RESET ALL CELLS
    // --------------------------------------------------------

    for (let i = 0; i < 16; i++) {

        const cell = document.querySelector(
            `.cell[data-index="${i}"]`
        );


        // ----------------------------------------------------
        // REMOVE AI HIGHLIGHT
        // ----------------------------------------------------

        cell.classList.remove(
            "ai-move",
            "winning-cell"
        );


        // ----------------------------------------------------
        // UPDATE CELL
        // ----------------------------------------------------

        updateCell(
            i
        );

    }


    // --------------------------------------------------------
    // ENABLE BOARD
    // --------------------------------------------------------

    setBoardDisabled(
        false
    );


    // --------------------------------------------------------
    // RESET MESSAGE
    // --------------------------------------------------------

    showStatus(
        "❌ New game started — your turn!"
    );

}


// ============================================================
// NEW GAME BUTTON EVENT
// ============================================================

newGameButton.addEventListener(
    "click",
    () => {

        startNewGame();

    }
);

// ============================================================
// SHOW GAME STATUS
// ============================================================

function showStatus(message) {


    resultElement.innerHTML = `
        <p>
            ${message}
        </p>
    `;

}