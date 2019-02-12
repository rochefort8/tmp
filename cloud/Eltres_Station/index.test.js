var index = require('./index');

var data = {
	"version": 1,
	"dataPayload": "0123456789abcdef0123456789abcdef",
	"lfourId": 1,
	"txTime": 1549531830869,
	"serviceTag": {
	    "service_id": "0000"
	}
};

data.txTime = Math.floor(new Date()); // ms

console.log(new Date()) ;


index.handler(data);
