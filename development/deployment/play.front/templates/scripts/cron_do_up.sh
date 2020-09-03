eval `ssh-agent -s` >/dev/null 2>/dev/null && ssh-add ~/github.ssh/github_do_rsa >/dev/null 2>/dev/null

cd ~/DataOcean
git fetch
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})


if [ $LOCAL != $REMOTE ]; then

    echo
    echo "****************************************"
    date
    echo "****************************************"
    echo

    echo 'LOCAL  :' $LOCAL
    echo 'REMOTE :' $REMOTE
    echo

    sh upgrade.sh

    echo
    echo "---------------------"
    echo "LANDING"
    echo "---------------------"
    echo

    cd ~/DataOcean/landing
    npm install
    npm run build

    sudo service nginx restart

fi
