'use strict';

var PR = require('./packet_receiver');
var packetReciever = new PR() ;

var PUBLISHER = require('./publisher') ;
var publisher = new PUBLISHER() ;

var CONVERTER = require('./payload_converter') ;
var payloadConverter = new CONVERTER ;

module.exports.handler = async (event, context) => {

    var arrivedPacket = event ;

    // Check whether the same packet had been already received
    const isDuplicated = await packetReciever.IsDuplicated(arrivedPacket) ;
    if (isDuplicated === true) {
        console.log("Disposing this packet...")
        return ;
    }

    // Change packet as we want
    var convertedPacket = payloadConverter.Convert(arrivedPacket) ;

    // Publish to MQTT broker with some additional data or modification
    publisher.Publish(convertedPacket);

    // Put this packet onto buffer to check duplication
    await packetReciever.Put(arrivedPacket) ;
    console.log('Put packet: ID=' 
        + arrivedPacket .lfourId + '/txTime=' + arrivedPacket.txTime);

    // Discard too old packets in DB
//    var timeBefore = packet.txTime - 1000*60*50 ;
    var timeBefore = arrivedPacket .txTime - 1000*60*5 ;
    await packetReciever.Discard(arrivedPacket ,timeBefore) ;

    return null;
}
