GLOBAL_URL=http://$(cat ../install/CNAME)

URLEVENT=$(curl -X POST -Ls -o /dev/null -w %{url_effective} $GLOBAL_URL)

date
echo $URLEVENT
START=$(date +%s)
curl \
-F "file=@test.zip" \
-Ls -o /dev/null \
$URLEVENT

echo "response in $(expr $(date +%s) - $START) seconds"
