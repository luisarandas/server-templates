

const protocol = window.location.protocol;
console.log(protocol);

const socket = io.connect(protocol + '//' + document.domain + ":" + location.port); //port + namespace);
console.log(socket);


socket.on('initialise', function(data) {});

async function send_server_and_back() {
    socket.emit("main_socket", "message_from_client"); 
    // [0] named function in app.py and [1] the data
}

socket.on('exchange', function(data) {
    // receive from the server
    console.log("received -> ", data)
});