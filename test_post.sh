URLEVENT=$(curl -X POST -Ls -o /dev/null -w %{url_effective} http://flask-env-jer.wtywmfbghe.us-west-2.elasticbeanstalk.com/)
echo "$URLEVENT"

curl \
-F "file=@test.jpg" \
$URLEVENT