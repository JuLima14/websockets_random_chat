var ENDPOINT = 'ws://127.0.0.1:9000/';

var socket;

var registry = {type: 'registry', value: ''};
var getUsersMessage = {type: 'users', value: ''};
var message = {type: 'message', value: '', to: '', from: ''};

var users = [];


function register() {
    socket = new WebSocket(ENDPOINT);

    socket.onopen = function(event) {
        registry.value = $('#name').val();
        socket.send(JSON.stringify(registry));
        socket.send(JSON.stringify(getUsersMessage));
    };

    socket.onmessage = function(event) {
        var reply = JSON.parse(event.data);

        if (reply.type === 'users') {
            users = reply.value;
            console.log('users are: ', users);
            showUsers();
        }

        if (reply.type === 'message') {
            addMessageToChat(reply.value, reply.from);
        }
    };

    $(window).unload(function(event) {
        socket.close();
    });
}

function sendMessage() {
    message.value = $('#message').val();
    message.to = $('#users').val()[0];
    socket.send(JSON.stringify(message));
    addMessageToChat(message.value, 'You');
}


/*
    Helper functions:
*/
function showUsers() {
    var select = $('#users');
    var userName = $('#name').val();
    var items;

    // clear select
    select.find('option').remove().end();

    // build options
    $.each(users, function(key, value){
        if (value !== userName) {
            items += '<option>' + value + '</option>';
        }
    });

    // append options
    select.append(items);
}

function registerAction() {
    $("#nameSection").addClass('hidden-xs-up');
    $("#usersSection").removeClass('hidden-xs-up');
}

function selectUserAction() {
    $("#usersSection").addClass('hidden-xs-up');
    $("#messageSection").removeClass('hidden-xs-up');
}

function addMessageToChat(msg, from) {
    $('#chat').append(from + ': ' + msg + '<br>');
}