#!/usr/bin/env bash
# create folder mounts
mkdir -p /tmp/data
mkdir -p /tmp/store
# if containers are running on different machines, use --add-host="name:ip" to redirect (ex: elk:x.x.x.x)
# start the database backend (runs on port 6379, mount a local volume that will store database)
docker run --name db -v /tmp/data:/data -d redis
# start the file store (mount a local volume that will store the intermediate files)
docker run --name store -v /tmp/store:/tmp/store -d witlox/store
# start the ELK stack (logstash on port 9200, kibana on port 9292, 9300 for worker logging)
docker run -p 9200:9200 -p 9300:9300 --name elasticsearch -v /tmp/data:/usr/share/elasticsearch/data -d elasticsearch
docker run -p 5000:5000 -it -d --name logstash --link elasticsearch:elasticsearch logstash logstash -e 'input { tcp { port => 5000 } } output { elasticsearch { host => elasticsearch } }'
docker run -p 5601:5601 --name kibana --link elasticsearch:elasticsearch -d kibana
# start uwsgi containers with overwritten config and mounted apps (ports 6000 & 7000)
docker run --name ilm --link db:db --link logstash:logstash -v $(pwd)/ilm.conf:/var/www/app/ilm.conf:ro -d witlox/ilm
docker run --name wjc --link db:db --link logstash:logstash -v $(pwd)/wjc.conf:/var/www/app/wjc.conf:ro -d witlox/wjc
# start nginx with the overwritten default site (port 80)
docker run -p 80:80 --name web --link kibana:kibana --link ilm:ilm --link wjc:wjc --link store:store -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro -d nginx
# and now everything should be up and running
