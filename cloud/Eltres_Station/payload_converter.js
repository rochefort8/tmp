'use strict'

var PayloadConverter = function (params) {

    if (!(this instanceof PayloadConverter)) {
      return new PayloadConverter(params);
    }
    this.Convert = function (packet) {

        // tx/rx time with "2019-02-11T08:56:09.442Z" format
        var rxTime = new Date(); 
        var txTime = new Date(packet.txTime);

        var newPacket = {
            'lfourId' : packet.lfourId,
            'txTime'  : packet.txTime,
            'dataPayload' : packet.dataPayload ,
            'bdkts' : {
                'data'     : packet.dataPayload ,
                'txTime' : txTime ,
                'rxTime' : rxTime
            }
        }

        // Any conversion here

        return newPacket ;

    }
}

module.exports = PayloadConverter ;