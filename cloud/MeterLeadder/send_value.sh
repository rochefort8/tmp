#!/bin/bash

#
# AWS IoT
#
cert="--cafile cert/rootCA.pem --cert cert/8c1da6513b-certificate.pem.crt --key cert/8c1da6513b-private.pem.key"
endpoint="a3c6t2xavixp02-ats.iot.ap-northeast-1.amazonaws.com"
topic="gauge/1"
#set -x

send_data() {
    value=$1
    date=`date "+%Y-%m-%dT%H:%M:%S"`
    json='{"date":'\"$date\"',"value":'$value'}'

    echo $json
    mosquitto_pub $cert -h $endpoint -p 8883 -q 1 -d -t $topic -i gauge1 -m $json 2>&1 | tee log.txt > /dev/null
}
    
while [ 1 ];
do
    let value=${RANDOM}*4/3276+20
    send_data $value
    sleep 3
done
