'use strict';

var vogels = require('vogels'),
    AWS    = vogels.AWS,
    _      = require('lodash'),
    util   = require('util'),
    Joi    = require('joi');

//AWS.config.loadFromPath(process.env.HOME + '/.ec2/credentials.json');
//
// When running this in local, set enviromnent valiables below,
// AWS_ACCESS_KEY_ID
// AWS_SECRET_ACCESS_KEY
// AWS_REGION=ap-northeast-1

var Packet = vogels.define('ELTRES-raw-packet', {
    hashKey : 'lfourId',
    rangeKey : 'txTime',
    schema : {
        lfourId     : Joi.number(),
        txTime      : Joi.number(),
        version     : Joi.number(),
        dataPayload : Joi.string(),
        serviceTag : {
            service_id  : Joi.string(),
        }
    }
});

var PacketReceiver = function (params) {

  if (!(this instanceof PacketReceiver)) {
    return new PacketReceiver(params);
  }
  this.IsDuplicated = async function (packet,callback) {
    var lfourId = packet.lfourId ;
    var txTime  = packet.txTime ;

    return new Promise(function(resolve, reject) {
      Packet.query(lfourId).where('txTime').eq(txTime) 
      .exec(function (err, resp) {
        if (err != null) {
            reject(err) ;
        }
        if ((resp != null) && (resp.Count > 0)) {
          console.log('Duplicated.¥n') ;
          resolve(true) ;
    //        console.log(util.inspect(_.pluck(resp.Items, 'attrs')));
        } else {
          resolve(false);
        }  
      });
    });
  }

  this.Put = function(packet) {
    params = JSON.stringify(packet) ;
    return new Promise(function(resolve, reject) {
      Packet.create(params, function (err, resp) {
        if (err != null) {
          reject(err) ;
        } else {
          resolve(0);
        } 
      }); 
    });
  }

  this.Discard = async function(packet,timeBefore) {
    var lfourId = packet.lfourId ;
  
    return new Promise(function(resolve, reject) {
      Packet.query(lfourId).where('txTime').lt(timeBefore) 
      .exec(function (err, resp) {
        if (err != null) {
            reject(err) ;
        }
        if ((resp != null) && (resp.Count > 0)) {

          // Try to remove all old packets
          for (let i = 0; i < resp.Count; i++) {
            var _lfourId = resp.Items[i].attrs.lfourId ;
            var _txTime  = resp.Items[i].attrs.txTime ;

            var key = { 'lfourId': _lfourId, 'txTime':_txTime} ;
            console.log('Packet ID=' + _lfourId + '/txTime=' + _txTime + ' had been removed.');
            Packet.destroy(_lfourId,_txTime, function (err, posts) {
//                console.log('Packet ID=' + _lfourId + '/txTime=' + _txTime + ' had been removed.');
            });
//            console.log(util.inspect(_.pluck(resp.Items[i], 'attrs')));
          }
          resolve(true) ;
        } else {
          resolve(false);
        }
      });
    });  
  }
}

module.exports = PacketReceiver ;