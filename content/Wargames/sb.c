#include <stdlib.h>

int main(int argc, char** argv) {
	
	setuid(988);

	system('/bin/bash');

	return 0;
}