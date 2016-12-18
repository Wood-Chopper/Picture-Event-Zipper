
for A in {1..50}
do
	mv test.jpg $A.jpg
	zip test.zip $A.jpg
	mv $A.jpg test.jpg
done

for A in {1..10}
do
	./bot.sh &
done
