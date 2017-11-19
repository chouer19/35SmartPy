
main : $(objects)
	g++ -c -lpthread -L. -luartdata -fPIC UARTlib.c -o UARTlib.o
	g++ -shared -Wl,-soname,UARTlib.so -o UARTlib.so UARTlib.o libuartdata.so
	
clean :
	rm -rf UARTlib.so UARTlib.o 
