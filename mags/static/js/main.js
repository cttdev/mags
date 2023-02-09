// Game State Enum
const GameState = Object.freeze({
    "IDLE": 0,
    "START": 1,
    "PLAYING": 2,
    "END": 3
});

// Global variables
var gameState = GameState.IDLE;

// Socket.io setup
var socket = io();

function onDrop(source, target, piece, newPos, oldPos, orientation) {
    socket.emit("move", source + target);
}

// Setup and config for chessboard.js
var board = Chessboard("board", {
    pieceTheme: "static/images/chesspieces/wikipedia/{piece}.png",
    draggable: true,
    onDrop: onDrop
    // sparePieces: true
})

// // Game State Listner
socket.on("update", function(data) {
    console.log(data);
    board.position(data);
});

socket.on("update_binary_board", function(data) {
    update_binary_board(data);
});

// var source = new EventSource("/game_state");
// source.onmessage = function(event) {
//     var data = JSON.parse(event.data);

//     // Unpack game state
//     var state = data.state;
//     var boardState = data.board;

//     // Update game state
//     gameState = state;
//     board.position(boardState);
// }


// Publishers for buttons
// Start game button publisher
document.getElementById("startBtn").onclick = function() {
    socket.emit("start");
}

// End game button publisher
document.getElementById("endBtn").onclick = function() {
    socket.emit("end");
}

function update_binary_board(data) {
    // Load the data json
    var data = JSON.parse(data);

    // Get all of the squares
    var raw_squares = document.getElementsByClassName("visualizer-node");

    // Loop through all of the squares
    for (var i = 0; i < raw_squares.length; i++) {
        // Get the square
        var square = raw_squares[i];

        // Get the square's id
        var squareId = square.id;

        // Get the square's value
        var squareValue = data[squareId.split("-")[1]];

        // Set the square's color
        if (squareValue == 1) {
            square.className = "btn btn-primary visualizer-node m-6";
        } else {
            square.className = "btn btn-secondary visualizer-node m-6";
        }
    }
}

// $('#startBtn').on("click", function() {
//         board.start();
//         // socket.emit("start");
// })
