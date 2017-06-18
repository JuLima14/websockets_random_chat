var ENDPOINT = 'http://localhost:5000/peers';
var KEY = 'gzgxxbw94e1m7vi';

var id;
var me;
var peers;
var peer;
var peerConnection;


$(function(){

    // generate my id
    $.post(ENDPOINT, function( data ) {
      id = data.id;
      console.log('ID is: ', id);

      // subscribe
        me = new Peer(id, {key: KEY});

        // listen messages
        me.on('connection', function(conn) {
          conn.on('data', function(data){
            console.log('message received! ', data);
          });
        });
    });

    // retrieve available peers list
    $.get(ENDPOINT, function( data ) {
      peers = data;
      console.log('Peers are: ', peers);
      showPeers();
    });


    $('form[name="peerForm"]').submit(function(event) {
        event.preventDefault();
        peer = $('#peers').val();
        console.log('Peer ID is: ', peer);
        selectPeerAction();

        peerConnection = me.connect(peer);
        peerConnection.on('open', function(){
          console.log('connection with peer established');
        });
    });

    $('form[name="messageForm"]').submit(function(event) {
        event.preventDefault();
        var message = $('#message').val();
        console.log('Message is: ', message);
        peerConnection.send(message);
        console.log('sent message');
    });

});

function showPeers() {
    var select = $('#peers');
    var items;

    // clear select
    select.find('option').remove().end();

    // build options
    $.each(peers, function(key, value){
        items += '<option>' + value + '</option>';
    });

    // append options
    select.append(items);
}

function selectPeerAction() {
    $("#peerForm").addClass('hidden-xs-up');
    $("#messageForm").removeClass('hidden-xs-up');
}

/*
var peer = new Peer('lkfd', {key: 'gzgxxbw94e1m7vi'});

var conn = peer.connect('lkfd2');
conn.on('open', function(){
  conn.send('hi!');
});
*/