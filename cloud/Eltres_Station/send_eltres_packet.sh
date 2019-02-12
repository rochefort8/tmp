#!/bin/bash

cert="--cacert cert/rootCA.pem --cert cert/certificate.pem.crt --key cert\
/private.pem.key"

endpoint="a3c6t2xavixp02-ats.iot.ap-northeast-1.amazonaws.com"
topic="eltres/bdkts/raw/1"
#set -x

send_data() {
    payload=$1
    id=$2

    echo %payload $id
    
    if [ -n $payload ]; then
       payload="0123456789abcdef0123456789abcdef"
    fi     
    if [ -n $id ]; then
       id="1"
    fi     

    
    tx=`date +%s000`
    json='{"version":1,"dataPayload":"'$payload'","lfourId":'$id',"txTime":'$tx',"serviceTag":{"service_id":"0000"}}'
    
    echo $json

    curl --tlsv1.2 -X POST $cert "https://"$endpoint":8443/topics/"$topic"?qos=1" -d $json 2>&1 | tee 
}
    
send_data $1 $2
