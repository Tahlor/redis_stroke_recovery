#!/bin/bash

#alias py="source /home/mason//Desktop/redis_stroke_recovery/venv/bin/activate"
export py="source /home/mason//Desktop/redis_stroke_recovery/venv/bin/activate"
_python="/home/mason//Desktop/redis_stroke_recovery/venv/bin/python"

# Start redis
cd /home/mason//BIG_DATA/redis/redis-5.0.8/src
nohup ./redis-server &
# TEST: redis-cli ping


# Start mongo
nohup sudo service mongd start &

#sudo systemctl unmask mongod
#sudo service mongod start



#Connect to VPN, setup matching port:
#89.187.185.46:10031
#handwriting.entrydns.org
#curl -k -X PUT -d "" https://entrydns.net/records/modify/CzUMa3gGghDAxHe12Bik

# Start up local website:

cd /home/mason/Desktop/redis_stroke_recovery
nohup $_python website.py &

# Check PORTS: 
sudo lsof -i -n  | grep 10031


# Start up Redis Queue workers:
cd /home/mason/Desktop/redis_stroke_recovery
nohup bash -c "$py && rq worker"



# Start the AI server:

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/mason/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/mason/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/home/mason/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/mason/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

#cd /home/mason//Desktop/simple_hwr/
#conda activate hwr
#python ./server/preds_server.py

read -p "Press enter to kill everything"
pkill -f "website.py"