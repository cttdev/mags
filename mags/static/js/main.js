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


// $('#startBtn').on("click", function() {
//         board.start();
//         // socket.emit("start");
// })
