document.addEventListener('DOMContentLoaded', () => {
    // --- Constants and State Variables ---
    const boardElement = document.getElementById('board');
    const cells = document.querySelectorAll('.cell');
    const gameMessage = document.getElementById('game-message');
    const playerStatus = document.getElementById('player-status');
    const aiStatus = document.getElementById('ai-status');
    const restartBtn = document.getElementById('restart-btn');
    const difficultySelect = document.getElementById('difficulty');
    const scorePlayerEl = document.getElementById('score-player');
    const scoreTiesEl = document.getElementById('score-ties');
    const scoreAiEl = document.getElementById('score-ai');

    const PLAYER = 'X';
    const AI = 'O';
    const EMPTY = '';

    // Internal board representation
    let boardState = Array(9).fill(EMPTY);
    let gameActive = true;
    let isPlayerTurn = true; // Player always goes first
    
    // Scores
    let scorePlayer = 0;
    let scoreTies = 0;
    let scoreAi = 0;

    // Winning combinations (indices)
    const winConditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
        [0, 4, 8], [2, 4, 6]             // Diagonals
    ];

    // --- Core UI Logic ---

    // Initialize Game
    function initGame() {
        boardState = Array(9).fill(EMPTY);
        gameActive = true;
        isPlayerTurn = true;

        // Reset UI
        cells.forEach(cell => {
            cell.innerText = '';
            cell.classList.remove('x', 'o', 'taken', 'win-highlight');
        });

        updateStatusDisplay();
        gameMessage.innerText = "Your Turn!";
        gameMessage.style.color = "var(--text-primary)";
    }

    // Handle a player's click
    function handleCellClick(e) {
        const cell = e.target;
        const index = parseInt(cell.getAttribute('data-index'));

        // Prevent action if cell is taken or game is over, or if it's not player's turn
        if (boardState[index] !== EMPTY || !gameActive || !isPlayerTurn) {
            return;
        }

        // 1. Player makes a move
        makeMove(index, PLAYER);

        // 2. Check if player won or drew
        if (checkGameOver(PLAYER)) return;

        // 3. AI's turn
        isPlayerTurn = false;
        updateStatusDisplay();
        gameMessage.innerText = "AI is thinking...";

        // Small delay to make it feel natural, not instant
        setTimeout(() => {
            if (!gameActive) return; // double check

            const bestAiMove = getBestMove(boardState);
            if (bestAiMove !== -1) {
                makeMove(bestAiMove, AI);
            }

            // 4. Check if AI won or drew
            if (checkGameOver(AI)) return;

            // 5. Back to player
            isPlayerTurn = true;
            updateStatusDisplay();
            gameMessage.innerText = "Your Turn!";
        }, 500);
    }

    // Apply a move to both internal state and DOM
    function makeMove(index, playerMark) {
        boardState[index] = playerMark;
        cells[index].innerText = playerMark;
        cells[index].classList.add(playerMark.toLowerCase(), 'taken');
    }

    // Update active indicators at the top
    function updateStatusDisplay() {
        if (isPlayerTurn) {
            playerStatus.classList.add('active');
            aiStatus.classList.remove('active');
        } else {
            aiStatus.classList.add('active');
            playerStatus.classList.remove('active');
        }
    }

    // Check game conditions
    function checkGameOver(lastPlayer) {
        const winCombo = getWinningCombo(boardState, lastPlayer);

        if (winCombo) {
            // End the game with a winner
            gameActive = false;
            highlightWinningCells(winCombo);

            if (lastPlayer === PLAYER) {
                gameMessage.innerText = "🎉 You Win!";
                gameMessage.style.color = "var(--accent-blue)";
                scorePlayer++;
                scorePlayerEl.innerText = scorePlayer;
            } else {
                gameMessage.innerText = "🤖 AI Wins!";
                gameMessage.style.color = "var(--accent-red)";
                scoreAi++;
                scoreAiEl.innerText = scoreAi;
            }
            return true;
        }

        if (isBoardFull(boardState)) {
            // End game as draw
            gameActive = false;
            gameMessage.innerText = "🤝 Match Draw!";
            gameMessage.style.color = "var(--text-secondary)";
            playerStatus.classList.remove('active');
            aiStatus.classList.remove('active');
            scoreTies++;
            scoreTiesEl.innerText = scoreTies;
            return true;
        }

        return false;
    }

    function highlightWinningCells(combo) {
        combo.forEach(index => {
            cells[index].classList.add('win-highlight');
        });
    }

    // --- Game Logic Helpers ---

    function getWinningCombo(board, player) {
        for (let combo of winConditions) {
            if (board[combo[0]] === player &&
                board[combo[1]] === player &&
                board[combo[2]] === player) {
                return combo;
            }
        }
        return null;
    }

    function checkWinner(board, player) {
        return getWinningCombo(board, player) !== null;
    }

    function isBoardFull(board) {
        return board.every(cell => cell !== EMPTY);
    }

    function getEmptyCells(board) {
        let emptyIndices = [];
        for (let i = 0; i < board.length; i++) {
            if (board[i] === EMPTY) {
                emptyIndices.push(i);
            }
        }
        return emptyIndices;
    }

    // --- Minimax AI Algorithm ---

    // The core recursive logic evaluating the board
    function minimax(board, depth, isMaximizing, alpha, beta) {
        // Base Scenarios
        if (checkWinner(board, AI)) return 10 - depth; // AI wins (faster is better)
        if (checkWinner(board, PLAYER)) return depth - 10; // Player wins (slower loss is better)
        if (isBoardFull(board)) return 0;          // Draw

        if (isMaximizing) {
            // AI ('O') wants to maximize score
            let bestScore = -Infinity;
            const available = getEmptyCells(board);

            for (let i of available) {
                board[i] = AI; // play
                let score = minimax(board, depth + 1, false, alpha, beta);
                board[i] = EMPTY; // undo

                bestScore = Math.max(score, bestScore);
                alpha = Math.max(alpha, bestScore);
                if (beta <= alpha) break; // Alpha-beta pruning
            }
            return bestScore;
        } else {
            // Player ('X') wants to minimize score
            let bestScore = Infinity;
            const available = getEmptyCells(board);

            for (let i of available) {
                board[i] = PLAYER; // play
                let score = minimax(board, depth + 1, true, alpha, beta);
                board[i] = EMPTY; // undo

                bestScore = Math.min(score, bestScore);
                beta = Math.min(beta, bestScore);
                if (beta <= alpha) break; // Alpha-beta pruning
            }
            return bestScore;
        }
    }

    // Calculate the best initial move for the AI
    function getBestMove(board) {
        const available = getEmptyCells(board);
        if (available.length === 0) return -1;
        
        const difficulty = difficultySelect.value;
        let makeRandomMove = false;
        
        if (difficulty === 'easy') {
            makeRandomMove = true; // 100% random
        } else if (difficulty === 'medium') {
            makeRandomMove = Math.random() < 0.5; // 50% random
        }

        if (makeRandomMove) {
            const randomIndex = Math.floor(Math.random() * available.length);
            return available[randomIndex];
        }

        let bestScore = -Infinity;
        let bestMove = -1;

        for (let i of available) {
            board[i] = AI; // play
            // Depth 0, next turn is minimizing (Player)
            let score = minimax(board, 0, false, -Infinity, Infinity);
            board[i] = EMPTY; // undo

            if (score > bestScore) {
                bestScore = score;
                bestMove = i;
            }
        }

        return bestMove;
    }

    // --- Event Listeners ---

    cells.forEach(cell => {
        cell.addEventListener('click', handleCellClick);
    });

    restartBtn.addEventListener('click', initGame);

    // Initial setup Call
    initGame();
});
