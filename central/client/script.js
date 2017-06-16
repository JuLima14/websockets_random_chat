var ENDPOINT = 'ws://127.0.0.1:9000/';

var socket;

var registry = {type: 'register', user: ''};
var createChat = {type: 'create_chat', name: ''};
var joinToChat = {type: 'join_to_chat', name: ''};
var sendMessageToChat = {type: 'send_message_to_chat', name: '', message: ''};

var users = [];
var chats = [];
var chat;


function register() {
    socket = new WebSocket(ENDPOINT);

    socket.onopen = function(event) {
        registry.user = $('#name').val();
        socket.send(JSON.stringify(registry));
    };

    socket.onmessage = function(event) {
        var reply = JSON.parse(event.data);

        if (reply.type === 'users') {
            users = reply.value;
            console.log('users are: ', users);
        }

        if (reply.type === 'chats') {
            chats = reply.value;
            console.log('chats are: ', chats);
            showChats();
        }

        if (reply.type === 'message') {
            addMessageToChat(reply.value, reply.sender);
        }

        if (reply.type === 'history') {
            $.each(reply.value, function(key, message){
                addMessageToChat(message.message, message.sender);
            });
        }
    };

    $(window).unload(function(event) {
        socket.close();
    });
}

function performChatCreation() {
    createChat.name = $('#chatName').val();
    chat = createChat.name;
    socket.send(JSON.stringify(createChat));
}

function performChatJoining(name) {
    joinToChat.name = name;
    chat = name;
    socket.send(JSON.stringify(joinToChat));
}

function sendMessage() {
    var messageInput = $('#message');
    sendMessageToChat.message = messageInput.val();
    sendMessageToChat.name = chat;
    socket.send(JSON.stringify(sendMessageToChat));

    messageInput.val('');
}

/*
    Helper functions:
*/
function showChats() {
    var select = $('#chats');
    var items;

    // clear select
    select.find('option').remove().end();

    // build options
    $.each(chats, function(key, value){
        items += '<option>' + value + '</option>';
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
    $('form[name="chatsForm"]').submit(function(event) {
        event.preventDefault();
        selectChatAction();
        var chatName = $('#chats').val();
        performChatJoining(chatName);
    });
    $('form[name="chatNameForm"]').submit(function(event) {
        event.preventDefault();
        selectChatAction();
        var chatName = $('#chatName').val();
        performChatCreation(chatName)
    });
    $('form[name="messageForm"]').submit(function(event) {
        event.preventDefault();
        sendMessage();
    });
});

function registerAction() {
    $("#nameForm").addClass('hidden-xs-up');
    $("#chatSection").removeClass('hidden-xs-up');
}

function selectChatAction() {
    $("#chatSection").addClass('hidden-xs-up');
    $("#messageForm").removeClass('hidden-xs-up');
}

function addMessageToChat(msg, sender) {
    $('#chat').append(sender + ': ' + msg + '<br>');
}
