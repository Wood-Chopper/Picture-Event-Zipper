
for A in {1..47}
do
	mv test.jpg $A.jpg
	zip test.zip $A.jpg
	mv $A.jpg test.jpg
done

for A in {1..20}
do
	sleep 60
	./bot.sh &
done
