cd ~/docean/src/Data_converter

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

    git pull

    ~/docean/bin/pip install -r requirements.txt
    ~/docean/bin/python manage.py migrate --noinput
    ~/docean/bin/python manage.py collectstatic --noinput

    sudo supervisorctl restart docean
    sudo service nginx restart

fi
