
link =-lpthread -L. -luartdata
main : $(objects)
	gcc -o main main.c $(link)
	
clean :
	rm -rf main main.o 
