mosquitto_pub --cafile cert/rootCA.pem --cert cert/8c1da6513b-certificate.pem.crt --key cert/8c1da6513b-private.pem.key -h a3c6t2xavixp02-ats.iot.ap-northeast-1.amazonaws.com -p 8883 -q 1 -d -t gauge/1 -i rochefort10 -m "Hello"
