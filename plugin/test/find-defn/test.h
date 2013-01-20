#pragma once

#include <iostream>

void in_other_tu();

inline void inline_header() {
	std::cout << "inline\n";
}

static void static_header() {
	std::cout << "static\n";
}

