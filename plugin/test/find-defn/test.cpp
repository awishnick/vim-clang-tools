#include <iostream>
#include "test.h"

void in_this_tu();

int main(int argc, char* argv[]) {
	in_other_tu();
	in_this_tu();
	inline_header();
	static_header();
	return 0;
}

void in_this_tu() {
	std::cout << "hey\n";
}
