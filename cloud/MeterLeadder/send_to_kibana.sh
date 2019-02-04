#!/bin/bash

#
# AWS IoT
#
url="https://search-smart-factory-fmrtdpk4ar5uis4nxaboif4vc4.ap-northeast-1.es.amazonaws.com/"
endpoint=$url"gauge/1/"
#set -x

send_data() {
    value=$1
    date=`date "+%Y-%m-%dT%H:%M:%S"`
    json='{"date":'\"$date\"',"value":'$value'}'

    echo $json
    curl $endpoint -X POST -H "Content-Type:application/json" -d $json 2>&1 | tee log.txt > /dev/null
}
    
while [ 1 ];
do
    let value=${RANDOM}*4/3276+20
    send_data $value
    sleep 3
    
done
