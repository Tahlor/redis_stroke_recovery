# redis_stroke_recovery


First, start redis:

    cd ~/BIG_DATA/redis/redis-5.0.8/src
    ./redis-server

Start Mongo:
    sudo systemctl unmask mongod
    sudo service mongd start
    

Connect to VPN, setup matching port:
    
    89.187.185.46:10031
    
    handwriting.entrydns.org
    curl -k -X PUT -d "" https://entrydns.net/records/modify/CzUMa3gGghDAxHe12Bik
    

Start up local website:

    cd Desktop/redis_stroke_recovery
    py
    python website.py

Start up Redis Queue workers:

    cd Desktop/redis_stroke_recovery
    py
    rq worker
    
Start the AI server:

    cd Desktop/simple_hwr
    conda activate hwr
    python pred_server.py

# Project
/home/mason/shares/galois/media/data/GitHub/redis


### Setup server forwarding
In apache config:`sudo nano /etc/apache2/sites-available/axon.cs.byu.edu.conf`

        ProxyPass /handwriting http://127.0.0.1:10034
        ProxyPassReverse /handwriting http://127.0.0.1:10034


### Use ssh
    option="-o StrictHostKeyChecking=no -o ServerAliveInterval=60 -o TCPKeepAlive=yes"
    command="/usr/bin/ssh -fNT -p 22 -L 10034:alexthelion-g10ac.cs.byu.edu:10031 tarch@schizo.cs.byu.edu -o StrictHostKeyChecking=no $option"

Make sure it worked:
    sudo lsof -i -P -n  | grep 10034