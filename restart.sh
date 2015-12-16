line=$(cat twistd.pid)
if [ ! $line ]; then
    echo "twisted is not run"
    twistd -y main.py
    echo "start twisted"
else
    kill $line
    twistd -y main.py -l logs/twistd.log --reactor=epoll
    echo "kill and restart twisted"
fi
exit 0

