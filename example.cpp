/*
This is a sample program to illustrate argument passing in C++ and enable the
run.sh script to compile and run a program.
*/
#include <iostream>

using namespace std;

int main(int argc, char* argv[])
{
	if(argc == 3)
	{
		cout << "The config file passed is: " << argv[1] << endl;

		cout << "The problem file passed is: " << argv[2] << endl;
	}else
	{
		cout << "Refering to a default case because there were not two arguments passed!" << endl;
	}

	return 0;
}