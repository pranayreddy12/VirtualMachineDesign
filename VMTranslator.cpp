#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>

using namespace std;
using std::ifstream;

int retCount = 0;

void printVec(vector<string> res) {
	for (auto el : res) {
		cout << el << endl;
	}
	cout << endl << endl   ;
}

void spPushFun(vector<string> & resString) {
	resString.push_back("@SP");
	resString.push_back("A=M");
	resString.push_back("M=D");
	resString.push_back("@SP");
	resString.push_back("M=M+1");
	resString.push_back("// END OF PUSH STATEMENT");
}

vector<string> fileAccess(string fileName) {
	vector<string> contents;
	ifstream indata;

	if (fileName.find('.') == std::string::npos) {
		fileName = fileName + "/Sys.vm";
	}
	cout << "infile name = " << fileName << endl;

	indata.open(fileName);

	if (!indata) {
		std::cerr << "Error:file could not be opened" << endl;
		exit(1);
	}

	string word;
	getline(indata, word);

	while (!indata.eof()) {
		while (getline(indata, word)) {
			if (word[0] != '/' && word[0] != ' ') {  // if it starts with comment or if there is a space remove
				contents.push_back(word);
			}
		}
	}

	indata.close();
	return contents;

}
void fileWrite(vector <string> lines, string fileName ) {
	ofstream myFile(fileName);
	if (myFile.is_open()) {
		for (auto line : lines) {
			myFile << line << "\n";
		}
	}
	else {
		cout << "unable to open file" << endl;
	}
}
vector<string> translate(vector<string> hackCommands) {
	vector<string> resString;
	for (string line : hackCommands) { 
		vector<string> commands;
		string word;
		stringstream ss(line);
		while (getline(ss, word, ' ')) {
			commands.push_back(word);
		}

		if (commands.size()) {
			string currFunction = "main";
			string prevFunction = "NULL";
			string locArgs = "0";
			if (commands[0] == "push") {											//// PUSH ////
				string numVal = commands[2];
				resString.push_back("// PUSH STATEMENT STARTS with " + commands[1] + "  and  " + commands[2]);

				if (commands[1] == "pointer") {
					if (numVal == "0") {
						resString.push_back("@THIS");
						resString.push_back("D=M");
					}
					else if (numVal == "1") {
						resString.push_back("@THAT");
						resString.push_back("D=M");
					}
				}
				else {
					resString.push_back('@' + numVal);
					resString.push_back("D=A");
					if (commands[1] != "constant") {				// IF NOT CONSTANT
						if (commands[1] == "local") {
							resString.push_back("@LCL");
						}
						else if (commands[1] == "argument") {
							resString.push_back("@ARG");
						}
						else if (commands[1] == "this") {
							resString.push_back("@THIS");
						}
						else if (commands[1] == "that") {
							resString.push_back("@THAT");
						}
						else if (commands[1] == "temp") {
							resString.push_back("@5");
						}
						else if (commands[1] == "static") {
							resString.push_back("@16");
						}
						if (commands[1] == "temp" || commands[1] == "static") {
							resString.push_back("D=A+D");
						}
						else
							resString.push_back("D=M+D");

						resString.push_back("A=D");
						resString.push_back("D=M");
					}
				}
				//spPushFun(resString);
				resString.push_back("@SP");
				resString.push_back("A=M");
				resString.push_back("M=D");
				resString.push_back("@SP");
				resString.push_back("M=M+1");
				resString.push_back("// END OF PUSH STATEMENT");
			}
			else if (commands[0] == "eq" || commands[0] == "lt" || commands[0] == "gt" || commands[0] == "neq" || commands[0] == "add" || commands[0] == "sub" || commands[0] == "and" || commands[0] == "or") {
				resString.push_back("@SP");
				resString.push_back("M=M-1");
				resString.push_back("@SP");
				resString.push_back("A=M");
				resString.push_back("D=M");
				resString.push_back("@SP");
				resString.push_back("M=M-1");
				resString.push_back("A=M");

				// WE POPPED 2 OF THEM ; ONE IS IN A ; OTHER IS IN D;
				if (commands[0] == "add" || commands[0] == "sub" || commands[0] == "and" || commands[0] == "or") {
					if (commands[0] == "add") {
						resString.push_back("D=D+M");
					}
					else if (commands[0] == "sub") {
						resString.push_back("D=M-D");
					}
					else if (commands[0] == "and") {
						resString.push_back("D=D&M");
					}
					else if (commands[0] == "or") {
						resString.push_back("D=D|M");
					}

					resString.push_back("@SP");
					resString.push_back("A=M");
					resString.push_back("M=D");

					// increment SP. 
					resString.push_back("@SP");
					resString.push_back("M=M+1");
				}
				else {

				}
			}
			else if (commands[0] == "not") {
				resString.push_back("@SP");
				resString.push_back("M=M-1");
				resString.push_back("@SP");
				resString.push_back("A=M");
				resString.push_back("D=!M");
				resString.push_back("@SP");
				resString.push_back("A=M");
				resString.push_back("M=D");
				// increment SP. 
				resString.push_back("@SP");
				resString.push_back("M=M+1");
			}
			else if (commands[0] == "pop") {								////////// POP ////////
				string numVal = commands[2];		//numVAl = 9
				resString.push_back("// POP Statement begins with " + commands[1] + "   and   "  + commands[2]);
				resString.push_back("@SP");
				resString.push_back("M=M-1");

				if (commands[1] == "pointer") {
					if (numVal == "0") {
						resString.push_back("@THIS");
						resString.push_back("D=A");
					}
					else if (numVal == "1") {
						resString.push_back("@THAT");
						resString.push_back("D=A");
					}
				}
				else {
					resString.push_back('@' + numVal);
					resString.push_back("D=A");

					if (commands[1] == "local") {
						resString.push_back("@LCL");
					}
					else if (commands[1] == "argument") {
						resString.push_back("@ARG");
					}
					else if (commands[1] == "this") {
						resString.push_back("@THIS");
					}
					else if (commands[1] == "that") {
						resString.push_back("@THAT");
					}
					else if (commands[1] == "temp") {
						resString.push_back("@5");
					}
					else if (commands[1] == "static") {
						resString.push_back("@16");
					}
					if (commands[1] == "temp" || commands[1] == "static")
						resString.push_back("D=A+D");
					else
						resString.push_back("D=M+D");
				}
					resString.push_back("@R13");
					resString.push_back("M=D");
					resString.push_back("@SP");
					resString.push_back("A=M");
					resString.push_back("D=M");
					resString.push_back("@R13");
					resString.push_back("A=M");
					resString.push_back("M=D");

					


			}
			else if (commands[0] == "label") {
				resString.push_back("(" + commands[1] + ")");
			}
			else if (commands[0] == "if-goto") {			// WHILE JUMPING REDUCE YOUR SP . POP THE ELEMENT OUT. 
				resString.push_back("@SP");
				resString.push_back("M=M-1");
				resString.push_back("A=M");
				resString.push_back("D=M");
				resString.push_back("@" + commands[1]);
				resString.push_back("D;JGT");
			}
			else if (commands[0] == "goto") {
				resString.push_back("@" + commands[1]);
				resString.push_back("D;JMP");
			}
			else if (commands[0] == "function") {
				prevFunction = currFunction;
				currFunction = commands[1];
				resString.push_back("("+ commands[1] + ")");
				locArgs = commands[2];
				resString.push_back("@" + locArgs);
				resString.push_back("D=A");
				resString.push_back("@SP");
				resString.push_back("M=M+D");
			}
			else if (commands[0] == "return") {
				//  R13 = LCL
				resString.push_back("@LCL");
				resString.push_back("D=M");
				resString.push_back("@R13");
				resString.push_back("M=D");

				// R14 = retAddr // retaddr = *(endframe - 5)
				resString.push_back("@5");
				resString.push_back("D=A");
				resString.push_back("@R13");
				resString.push_back("A=M-D");
				resString.push_back("D=M");
				resString.push_back("@R14");
				resString.push_back("M=D");

				// *ARG = pop()
				resString.push_back("@SP");
				resString.push_back("M=M-1");
				resString.push_back("@SP");
				resString.push_back("A=M");
				resString.push_back("D=M");
				resString.push_back("@ARG");
				resString.push_back("A=M");
				resString.push_back("M=D");

				// SP = ARG + 1
				resString.push_back("@ARG");
				resString.push_back("D=M");
				resString.push_back("@SP");
				resString.push_back("M=D+1");

				// THAT = *(endframe -1 )
				resString.push_back("@R13");
				resString.push_back("D=M-1");
				resString.push_back("A=D");
				resString.push_back("D=M");
				resString.push_back("@THAT");
				resString.push_back("M=D");

				// THIS = *(endframe -2 )
				resString.push_back("@2");
				resString.push_back("D=A");
				resString.push_back("@R13");
				resString.push_back("D=M-D");
				resString.push_back("A=D");
				resString.push_back("D=M");
				resString.push_back("@THIS");
				resString.push_back("M=D");

				// ARG = *(endframe -3 )
				resString.push_back("@3");
				resString.push_back("D=A");
				resString.push_back("@R13");
				resString.push_back("D=M-D");
				resString.push_back("A=D");
				resString.push_back("D=M");
				resString.push_back("@ARG");
				resString.push_back("M=D");

				// LCL = *(endframe -4 )
				resString.push_back("@4");
				resString.push_back("D=A");
				resString.push_back("@R13");
				resString.push_back("D=M-D");
				resString.push_back("A=D");
				resString.push_back("D=M");
				resString.push_back("@LCL");
				resString.push_back("M=D");
				
				if (retCount != 0) {
					resString.push_back("@R14");
					resString.push_back("A=M");
					resString.push_back("0,JMP");
					retCount--;
				}
			
			}
			else if (commands[0] == "call") {
			resString.push_back("//call statement begin");
				string nArgs = commands[2];
				string callFunction = commands[1];
				retCount++;
				// Push return address
				string retAddress = "@test";
				retAddress += to_string(retCount);
				//retAddress.push_back(to_string(retCount));
				resString.push_back(retAddress);
				resString.push_back("D=A");
				spPushFun(resString);

				// push LCL
				resString.push_back("@LCL");
				resString.push_back("D=M");
				spPushFun(resString);

				// push ARG
				resString.push_back("@ARG");
				resString.push_back("D=M");
				spPushFun(resString);

				// push THIS
				resString.push_back("@THIS");
				resString.push_back("D=M");
				spPushFun(resString);

				// push THAT
				resString.push_back("@THAT");
				resString.push_back("D=M");
				spPushFun(resString);

				// ARG = SP - 5 - nArgs
				resString.push_back("@SP");
				resString.push_back("D=M");
				resString.push_back("@5");
				resString.push_back("D=D-A");
				resString.push_back("@" + nArgs);
				resString.push_back("D=D-A");
				
				resString.push_back("@ARG");
				resString.push_back("M=D");

				// LCL = SP
				resString.push_back("@SP");
				resString.push_back("D=M");
				resString.push_back("@LCL");
				resString.push_back("M=D");

				//  goto functionname
				resString.push_back("@" + callFunction);
				resString.push_back("0; JMP");

				resString.push_back("(test" + to_string(retCount) + ")");
			}
		}
	}
	// END STATEMENTS. 
	resString.push_back("//// END LOOP");
	resString.push_back("(END)");
	resString.push_back("@END");
	resString.push_back("0;JMP");
	//printVec(commands);
	return resString;

}

int main(int argc, char* argv[]) {

	string inFileName;
	string outFileName;
	cout << "argc = " << argc << endl;
	if (argc != 2) {
		cout << "Wrong command line arguments passed" << endl;
		return 0;

	}
	else {
		bool isDir = 1;
		inFileName = argv[1];
		for (auto ch : inFileName) {
			if (ch != '.') {
				outFileName.push_back(ch);
			}
			else {
				isDir = 0;
				break;
			}
		}
		if (inFileName.find('.') == std::string::npos) {
			outFileName = outFileName + "/" + outFileName + ".asm";
		}
		else {
			outFileName+=".asm";
		}
	}
	vector<string> words;
	words = fileAccess(inFileName);
	vector<string> commands = translate(words);
	printVec(commands);
	fileWrite(commands, outFileName);
	return 0;
}
