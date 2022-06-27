

// luis arandas 27-06-2022

const protocol = window.location.protocol;
const socket = io.connect(protocol + '//' + document.domain + ":" + location.port); //port + namespace);


socket.on('initialise', function(data) {});

async function send_server_and_back() {
    socket.emit("main_socket", "ola"); 
    // [0] named function in app.py and [1] the data
}

socket.on('exchange', function(data) {
    // receive from the server
    console.log("received -> ", data)
});