
main : $(objects)
	g++ -c -lpthread -L. -luartdata -fPIC CANlib.c -o CANlib.o
	g++ -shared -Wl,-soname,CANlib.so -o CANlib.so CANlib.o libuartdata.so
	
clean :
	rm -rf CANlib.so CANlib.o 
