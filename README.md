# redis_stroke_recovery


First, start redis:

    cd ~/BIG_DATA/redis/redis-5.0.8/src
    ./redis-server

Start Mongo:

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


