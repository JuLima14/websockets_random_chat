var ENDPOINT = 'ws://127.0.0.1:9000/';

var socket;

var registry = {type: 'registry', value: ''};
var message = {type: 'message', value: '', to: '', from: ''};

var users = [];


function register() {
    socket = new WebSocket(ENDPOINT);

    socket.onopen = function(event) {
        registry.value = $('#name').val();
        socket.send(JSON.stringify(registry));
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

$(function(){
    $('form[name="nameForm"]').submit(function(event) {
        event.preventDefault();
        registerAction();
        register();
    });
    $('form[name="usersForm"]').submit(function(event) {
        event.preventDefault();
        selectUserAction();
    });
    $('form[name="messageForm"]').submit(function(event) {
        event.preventDefault();
        sendMessage();
    });
});

function registerAction() {
    $("#nameForm").addClass('hidden-xs-up');
    $("#usersForm").removeClass('hidden-xs-up');
}

function selectUserAction() {
    $("#usersForm").addClass('hidden-xs-up');
    $("#messageForm").removeClass('hidden-xs-up');
}

function addMessageToChat(msg, from) {
    $('#chat').append(from + ': ' + msg + '<br>');
}