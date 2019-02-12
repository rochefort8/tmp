'use strict';

const TOPIC='eltres/bdkts/wrapped/1',
      URL='https://a3c6t2xavixp02-ats.iot.ap-northeast-1.amazonaws.com:8443/';

const fs = require('fs')
    , path = require('path')
    , certFile = path.resolve(__dirname, 'cert/certificate.pem.crt')
    , keyFile = path.resolve(__dirname, 'cert/private.pem.key')
    , caFile = path.resolve(__dirname, 'cert/rootCA.pem');

var request = require('request');

var Publisher = function (params) {

    if (!(this instanceof Publisher)) {
      return new Publisher(params);
    }

    this.Publish= async function(packet) {
        var options = {
            url: URL + 'topics/' + TOPIC + '?qos=1',
            method: 'POST',
            secureProtocol: "TLSv1_2_method",
            cert: fs.readFileSync(certFile),
            key: fs.readFileSync(keyFile),
            ca: fs.readFileSync(caFile),
            body: JSON.stringify(packet)
        };

        return new Promise(function(resolve, reject) {
            request(options,function (error, response, body) {
                if (!error && response.statusCode == 200) {
                    console.log(body);
                    resolve(0);
                } else {
                    console.log(error);
                    reject(error);
                }
            }); 
        });
    }
}

module.exports = Publisher ;

