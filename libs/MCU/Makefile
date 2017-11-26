
main : $(objects)
	g++ -c -lpthread -L. -luartdata -fPIC MCUlib.c -o MCUlib.o
	g++ -shared -Wl,-soname,MCUlib.so -o MCUlib.so MCUlib.o libuartdata.so
	
clean :
	rm -rf MCUlib.so MCUlib.o 
