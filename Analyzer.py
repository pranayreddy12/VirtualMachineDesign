

import os;
import sys;
import re;


jackFilePath = sys.argv[1]
print(jackFilePath)

try:
    jackPtr = open(jackFilePath,"r+");
except:
    print("Error");
    sys.exit(2);

outPath = (sys.argv[1][:-5] + "T1" + ".xml")
print(outPath)
outPtr = open(outPath, "w");

outPtr.write("<tokens>")
outPtr.write('\n');

tokenDict = {
    "class"         :"keyword",
    "constructor"   :"keyword",
    "function"      :"keyword",
    "method"        :"keyword",
    "field"         :"keyword",
    "static"        :"keyword",
    "var"           :"keyword",
    "int"           :"keyword",
    "char"          :"keyword",
    "boolean"       :"keyword",
    "void"          :"keyword",
    "true"          :"keyword",
    "false"         :"keyword",
    "null"          :"keyword",
    "this"          :"keyword",
    "let"           :"keyword",
    "do"            :"keyword",
    "if"            :"keyword",
    "else"          :"keyword",
    "while"         :"keyword",
    "return"        :"keyword",
    "{"             :"symbol",
    "}"             :"symbol",
    ")"             :"symbol",
    "("             : "symbol",
    "["             : "symbol",
    "]"             : "symbol",
    "."             : "symbol",
    ","             : "symbol",
    ";"             : "symbol",
    "+"             : "symbol",
    "-"             : "symbol",
    "*"             : "symbol",
    "/"             : "symbol",
    "&"             : "symbol",
    "|"             : "symbol",
    "<"             : "symbol",
    ">"             : "symbol",
    "="             : "symbol",
    "~"             : "symbol"
}

compDict = {
    "<" : "&lt;",
    ">" : "&gt;",
    "&" : "&amp;"    
}



def processWord(word):
    #print("processing ... ", word);
    word = word.strip();

    if(len(word) == 0):
        return;

    if ('(' in word):
        bMatchx = re.match("(.*)\((.*)\)(.*)", word);
        if (bMatchx):
            processWord(bMatchx.group(1));
            outPtr.write("<symbol> ")
            outPtr.write("(")
            outPtr.write(" </symbol>")
            outPtr.write('\n');
            processWord(bMatchx.group(2));
            outPtr.write("<symbol> ")
            outPtr.write(")")
            outPtr.write(" </symbol>")
            outPtr.write('\n');
            processWord(bMatchx.group(3));
        else:
            bMatchx1 = re.match("(.*)\((.*)", word);
            if (bMatchx1):
                processWord(bMatchx1.group(1));
                outPtr.write("<symbol> ")
                outPtr.write("(")
                outPtr.write(" </symbol>")
                outPtr.write('\n');
                processWord(bMatchx1.group(2));
    elif (')' in word):
            lbMatchx = re.match("(.*)\)(.*)", word);
            if (lbMatchx):
                processWord(lbMatchx.group(1));
                outPtr.write("<symbol> ")
                outPtr.write(")")
                outPtr.write(" </symbol>")
                outPtr.write('\n');
                processWord(lbMatchx.group(2));
    elif (' ' in word):
        words = word.split(' ');
        for newWord in words:
            processWord(newWord);
    elif(';' in word):
        processWord(word[:-1]);
        outPtr.write("<symbol> ");
        outPtr.write(";")
        outPtr.write(" </symbol>");
        outPtr.write('\n');
    elif('.' in word):
        words = word.split('.');
        totCount = len(words);
        count = 1;
        for newWord in words:
            processWord(newWord);
            if(count == totCount):
                break;
            outPtr.write("<symbol> ");
            outPtr.write(".")
            outPtr.write(" </symbol>");
            outPtr.write('\n');
            count+=1;
    elif (',' in word):
        words = word.split(',');
        totCount = len(words);
        count = 1;
        for newWord in words:
            processWord(newWord);
            if (count == totCount):
                break;
            outPtr.write("<symbol> ");
            outPtr.write(",")
            outPtr.write(" </symbol>");
            outPtr.write('\n');
            count += 1;
    elif('[' in word):
        bMatch = re.match("^(.*)\[(.+)\](.*)$", word);
        if(bMatch):
            processWord(bMatch.group(1));
            outPtr.write("<symbol> ")
            outPtr.write("[")
            outPtr.write(" </symbol>")
            outPtr.write('\n');
            processWord(bMatch.group(2));
            outPtr.write("<symbol> ")
            outPtr.write("]")
            outPtr.write(" </symbol>")
            outPtr.write('\n');
            processWord(bMatch.group(3));
    elif (word in tokenDict):
        if(word in compDict):
            newWord = compDict[word];
        else:
            newWord = word;
        outPtr.write("<" + tokenDict[word] + "> ")
        outPtr.write(newWord)
        outPtr.write(" </" + tokenDict[word] + ">")
        outPtr.write('\n');
    elif (re.match("^[0-9]+$", word)):
        outPtr.write("<" + "integerConstant" + "> ")
        outPtr.write(word)
        outPtr.write(" </" + "integerConstant" + ">")
        outPtr.write('\n')
    elif (re.match("([0-9]|[a-z]|[A-Z]|_)", word)):
        outPtr.write("<" + "identifier" + "> ")
        outPtr.write(word)
        outPtr.write(" </" + "identifier" + ">")
        outPtr.write('\n')
    elif (re.match("-(.*)", word)):
        outPtr.write("<" + "symbol" + "> ")
        outPtr.write('-')
        outPtr.write(" </" + "symbol" + ">")
        outPtr.write('\n')
        processWord(word[1:]);
    elif(re.match("([\&|\~|\!])(.*)", word)):
        iMatch = re.match("([\&|\~|\!])(.*)", word);
        if(iMatch):
            outPtr.write("<" + "symbol" + "> ")
            outPtr.write(iMatch.group(1));
            outPtr.write(" </" + "symbol" + ">")
            outPtr.write('\n')
            outPtr.write("<" + "identifier" + "> ")
            outPtr.write(iMatch.group(2));
            outPtr.write(" </" + "identifier" + ">")
            outPtr.write('\n')


def tokenizer():
    blockComm = 0;

    for line in jackPtr:
        print(line, "  bcome = ", blockComm)
        line = line.strip();
        addId = 0;

        ## REMOVE COMMENTS.
        if(re.match("^\/\/", line)):
            continue;

        if(re.match("^\/\*", line) and not(re.match(".+\*\/$", line))):
            blockComm = 1;
            continue;

        if (re.match(".*\*\/$", line)):
            blockComm = 0;
            continue;

        if(blockComm):
            continue;

        ## REMOVE Empty lines.
        if(re.match("^\s+$", line)):
            continue;

        ## REMOVE Comments after lines.
        cmLine = re.match("^(.*)\/\/", line);
        if (cmLine):
            line = cmLine.group(1);

        ## UPdate the string stuff.
        mString = re.match("^(.*)\"(.*)\"(.*)$", line);
        if(mString):
            #print("gp1 = ", mString.group(1), " gp 2 = ", mString.group(2));
            processWord(mString.group(1));
            outPtr.write("<" + "stringConstant" + "> ")
            outPtr.write(mString.group(2));
            outPtr.write(" </" + "stringConstant" + ">")
            outPtr.write('\n')
            processWord(mString.group(3));
            continue;

        ## CHECK FOR ALL BRACKETS. 
        
        if ('(' in line):
            bMatch = re.match("(.*)\((.*)\)(.*)", line);
            if (bMatch):
                processWord(bMatch.group(1));
                outPtr.write("<symbol> ")
                outPtr.write("(")
                outPtr.write(" </symbol>")
                outPtr.write('\n');
                processWord(bMatch.group(2));
                outPtr.write("<symbol> ")
                outPtr.write(")")
                outPtr.write(" </symbol>")
                outPtr.write('\n');
                processWord(bMatch.group(3));
                continue;
            else:
                bMatch1 = re.match("(.*)\((.*)", line);
                if (bMatch1):
                    processWord(bMatch1.group(1));
                    outPtr.write("<symbol> ")
                    outPtr.write("(")
                    outPtr.write(" </symbol>")
                    outPtr.write('\n');
                    processWord(bMatch1.group(2));
                    continue;
        elif (')' in line):
            lbMatch = re.match("(.*)\)(.*)", line);
            if (lbMatch):
                processWord(lbMatch.group(1));
                outPtr.write("<symbol> ")
                outPtr.write(")")
                outPtr.write(" </symbol>")
                outPtr.write('\n');
                processWord(lbMatch.group(2));
                continue;
      
        ## SPLIT THE LINE INTO WORDS.
        words = line.split(' ');
        wordStart = 0;
        stringName = ""

        for word in words:
            processWord(word)

    outPtr.write("</tokens>")





class CompilationEngine:

    def __init__(self, filePath):
        self.jackPtr   = open(filePath,"r+").read();
        self.jackLines = self.jackPtr.split('\n');
        self.currLineNum = 0;
        self.tab = 0;
        self.outputFile  = sys.argv[1][:-5] + "1" + ".xml";
        self.comPtr = open(self.outputFile, "w");
        self.maxLines = 0;
        self.tmpFile  = sys.argv[1][:-5] + "tmp" + ".xml";
        self.tmpPtr = open(self.tmpFile, "w");

    def updatePtr(self):
        self.jackPtr   =open(self.tmpFile, "r+").read();
        self.jackLines = self.jackPtr.split('\n');
        self.maxLines = len(open(self.tmpFile).readlines(  ))

    def lineWrite(self, instring):
        for num in range(self.tab):
            self.comPtr.write("  ");
        self.comPtr.write(instring)
        self.comPtr.write("\n");

    def processFile(self):

        block = 0;
        for line in self.jackLines:
            line = line.strip();
            if(line == ""):
                continue;
            if("//" in line):
                if(re.match("^\/\/.*", line)):
                    continue;
                else:
                    newLine = re.match("(.*)\/\/.*", line).group(1).strip();
                    if(newLine != ""):
                        self.tmpPtr.write(newLine);
                        self.tmpPtr.write("\n");
                    continue;
            if("/*" in line):
                block = 1;
            if("*/" in line):
                block = 0;
                continue;
            if(block):
                continue;
            else:
                self.tmpPtr.write(line);
                self.tmpPtr.write("\n");


        self.tmpPtr.close();

    def advance(self):
        currLine = self.jackLines[self.currLineNum].strip();
        print(currLine);
        if("//" in currLine):
            if(re.match("^\/\/.*", currLine)):
                self.currLineNum+=1;
                return;
            else:
                self.jackLines[self.currLineNum] = re.match("(.*)\/\/.*", currLine).group(1);
                return;

        if("/*" in currLine):
            while("*/" not in currLine):
                self.currLineNum+=1;
            self.currLineNum+=1;
            return;

        if("class" in currLine):
            self.compileClass();
            self.currLineNum+=1;
            return;

        self.currLineNum+=1;

    def ifEnd(self):
        if(self.currLineNum == len(self.jackLines)):
            return True;
        else:
            return False;



    def compileClass(self):
        currLine = self.jackLines[self.currLineNum].strip();
        
        clMatch = re.match("class (.*) {", currLine);
        print("in class method");
        
        self.lineWrite("<class>");
        self.tab+=1;
        self.lineWrite("<keyword> class </keyword>");
        self.lineWrite("<identifier> "+ clMatch.group(1) + " </identifier>");
        self.lineWrite("<symbol> { </symbol>");
        self.currLineNum+=1;
        currLine = self.jackLines[self.currLineNum].strip();
        
        while('static' in currLine or 'field' in currLine):
            self.compileClassVarDec();
            currLine = self.jackLines[self.currLineNum].strip();

        while('}' not in currLine):
            self.compileSubRoutineDec();
            currLine = self.jackLines[self.currLineNum].strip();

        self.lineWrite("<symbol> } </symbol>");
        self.tab-=1;
        self.lineWrite("</class>");

    def compileVars(self, currWord):
        currWord = currWord.strip();
        varMatch = re.match("([^,]+)\,([^,]+)", currWord)
        if(varMatch):
            self.lineWrite("<identifier> " + varMatch.group(1) + " </identifier>")
            self.lineWrite("<symbol> , </symbol>")
            self.compileVars(varMatch.group(2))
        else:
            self.lineWrite("<identifier> " + currWord + " </identifier>")

    def compileClassVarDec(self):
        print("in class var dec")
        self.lineWrite("<classVarDec>")
        self.tab+=1;
        currLine = self.jackLines[self.currLineNum].strip();
        print("in class var dec", currLine);
        mClass = re.match("^(\S+) (\S+) (.*);", currLine)

        if(mClass):
            self.lineWrite("<keyword> "+ mClass.group(1) + " </keyword>");      ## STATIC / FIELD.
            if(mClass.group(2) in ['int','char','boolean']):
                self.lineWrite("<keyword> "+ mClass.group(2) + " </keyword>")       
            else:
                self.lineWrite("<identifier> "+ mClass.group(2) + " </identifier>")
            self.compileVars(mClass.group(3));
            self.lineWrite("<symbol> ; </symbol>")

        self.currLineNum+=1;
        self.tab-=1;
        self.lineWrite("</classVarDec>")

    def compileSubRoutineDec(self):
        currLine = self.jackLines[self.currLineNum].strip();
        print(" in subroutine dec method .. ", currLine);
        mRotMatch = re.match("^(function|method|constructor) (\S+) (\S+)\((.*)\).*", currLine)
        retType = "";
        funName = "";
        args    = "";
        if(mRotMatch):
            retType = mRotMatch.group(2).strip();
            funName = mRotMatch.group(3).strip();
            args    = mRotMatch.group(4).strip();

            self.lineWrite("<subroutineDec>")
            self.tab+=1;
            self.lineWrite("<keyword> "+  mRotMatch.group(1).strip() +" </keyword>")
            self.lineWrite("<keyword> " + retType +  " </keyword>");
            self.lineWrite("<identifier> " + funName +  " </identifier>");
            self.lineWrite("<symbol> " + '(' +  " </symbol>");

            self.compileParameterList(args);

            self.lineWrite("<symbol> " + ')' +  " </symbol>");

            self.compileSubRoutineBody();

        self.tab-=1;
        self.lineWrite("</subroutineDec>")


    def compileParameterList(self, args):
        print(" in parameter list");
        self.lineWrite("<parameterList>")
        self.lineWrite("</parameterList>")

    def compileSubRoutineBody(self):
        print(" in sub routine body");
        self.lineWrite("<subroutineBody>")
        self.tab+=1;
        self.lineWrite("<symbol> { </symbol>")

        self.currLineNum+=1;

        currLine = self.jackLines[self.currLineNum].strip();
        while("var" in currLine):
            self.compileVarDec(currLine);
            currLine = self.jackLines[self.currLineNum].strip();

        
        self.compileStatements();
        currLine = self.jackLines[self.currLineNum].strip();
        self.lineWrite("<symbol> } </symbol>")
        self.tab-=1;
        self.lineWrite("</subroutineBody>")
        print(" out of sub routine body")



    def compileVarDec(self, currLine):
        print(" in var dec");
        vMatch = re.match("var (\S+) (.*);", currLine);

        if(vMatch):
            self.lineWrite("<varDec>")
            self.tab+=1;
            self.lineWrite("<keyword> var </keyword>")
            if(vMatch.group(1) in ["int", "char", "boolean"]):
                self.lineWrite("<keyword> " + vMatch.group(1) + " </keyword>") 
            else:
                self.lineWrite("<identifier> " + vMatch.group(1) + " </identifier>") 
            self.compileVars(vMatch.group(2));
            self.lineWrite("<symbol> ; </symbol>")
            self.tab-=1;
            self.lineWrite("</varDec>")

        self.currLineNum+=1   
   
    def compileSubRoutineCall(self, currWord):
        print("in sub routine call", currWord)
        subMatch = re.match("(.*)\.(.*)\((.*)\)", currWord);

        if(not subMatch):
            sbMatch1 = re.match("(.*)\((.*)\)", currWord);
            self.lineWrite("<identifier> " + sbMatch1.group(1) + " </identifier>");
            self.lineWrite("<symbol> ( </symbol>");
            self.compileExpressionList(sbMatch1.group(2));
            self.lineWrite("<symbol> ) </symbol>");
        else:
            self.lineWrite("<identifier> " + subMatch.group(1) + " </identifier>");
            self.lineWrite("<symbol> . </symbol>");
            self.lineWrite("<identifier> " + subMatch.group(2) + " </identifier>");
            self.lineWrite("<symbol> ( </symbol>");
            self.compileExpressionList(subMatch.group(3));
            self.lineWrite("<symbol> ) </symbol>");

    def compileDoStatement(self, currLine):
        print(" in do function");
        self.lineWrite("<doStatement>")
        self.tab+=1;
        self.lineWrite("<keyword> do </keyword>")
        doMatch = re.match("do (.*)", currLine);
        if(doMatch):
            self.compileSubRoutineCall(doMatch.group(1))
        self.lineWrite("<symbol> ; </symbol>")
        self.tab-=1;
        self.lineWrite("</doStatement>")

    def compileReturn(self, currLine):
        print(" in return function");
        self.lineWrite("<returnStatement>")
        self.tab+=1;
        retMatch = re.match("return (.*);", currLine)
        self.lineWrite("<keyword> return </keyword>")
        if(retMatch and retMatch.group(1)):
            self.compileExpression(retMatch.group(1));
        self.lineWrite('<symbol> ; </symbol>')
        self.tab-=1
        self.lineWrite("</returnStatement>")
        print(" out of return function");


    def compileExpressionList(self, currWord):
        print(" in expression list function");
        self.lineWrite("<expressionList>")
        self.lineWrite("</expressionList>")

    def compileStatements(self):
        print("in general statement");
        currLine = self.jackLines[self.currLineNum].strip();

        self.lineWrite("<statements>")
        self.tab+=1;

        print(self.maxLines)

        while('}' not in currLine and self.currLineNum < self.maxLines - 1):
            print("extracting gen", currLine)
            if('let' in currLine):
                self.compileLetStatement();
            elif('do' in currLine):
                self.compileDoStatement(currLine);
            elif('if' in currLine):
                self.compileIfStatement();
            elif('while' in currLine):
                self.compileWhileStatements();
            elif('var' in currLine):
                self.compileVarDec(currLine)
            elif('return' in currLine):
                self.compileReturn(currLine)
            self.currLineNum+=1;
            currLine = self.jackLines[self.currLineNum].strip();

        self.currLineNum+=1;
        self.tab-=1;
        self.lineWrite("</statements>")
        print("out of general statement");


    def compileIfStatement(self):
        print("in IF");
        currLine = self.jackLines[self.currLineNum].strip();

        ifMatch = re.match("if \((.*)\) {",currLine )
        if(ifMatch):
            self.lineWrite("<ifStatement>");
            self.tab+=1;
            self.lineWrite("<keyword> if </keyword>");
            self.lineWrite("<symbol> ( </symbol>");
            self.compileExpression(ifMatch.group(1));
            self.lineWrite("<symbol> ) </symbol>");
            self.lineWrite("<symbol> { </symbol>");
            self.currLineNum+=1;
            self.compileStatements();
            self.lineWrite("<symbol> } </symbol>");
            print(" INNN IFF",self.jackLines[self.currLineNum].strip())
            if('else' in self.jackLines[self.currLineNum].strip()):
                self.lineWrite("<keyword> else </keyword>");
                self.lineWrite("<symbol> { </symbol>");
                self.currLineNum+=1;
                self.compileStatements();
                self.lineWrite("<symbol> } </symbol>");

            self.tab-=1;
            self.lineWrite("</ifStatement>");
        print("Out of IF");

            
    
    def compileLetStatement(self):
        print("in Let");
        currLine = self.jackLines[self.currLineNum].strip();
        lMatch = re.match("let (\S+) = (.*);", currLine);
        if(lMatch):
            self.lineWrite("<letStatement>")
            self.tab+=1;
            self.lineWrite("<keyword> let </keyword>");

            if(re.match("let (.*)\[(.*)\] =.*", currLine)):
                mSq = re.match("let (.*)\[(.*)\] =.*", currLine)
                self.lineWrite("<identifier> " + mSq.group(1) + " </identifier>")
                self.lineWrite("<symbol> [ </symbol>")
                self.compileExpression(mSq.group(2))
                self.lineWrite("<symbol> ] </symbol>")
            else:
                self.lineWrite("<identifier> "+ lMatch.group(1)+" </identifier>");
            
            self.lineWrite("<symbol> = </symbol>")
            self.compileExpression(lMatch.group(2));

            self.lineWrite("<symbol> ; </symbol>");
            self.tab-=1;
            self.lineWrite("</letStatement>");


    def compileTerm(self, currWord):
        currWord = currWord.strip();
        print("in term", currWord)
        self.lineWrite("<term>")
        self.tab+=1;
        #re.match();
        
        if(re.match("^[\d]+$", currWord)):                                              ## DECIMAL
            self.lineWrite("<integerConstant> "+currWord+" </integerConstant>")
        elif(currWord in ["true", "false", "null", "this"]):
            self.lineWrite("<keyword> "+currWord+" </keyword>")
        elif(re.match("^[\w]+$",currWord)):                                              ## Key word constant
            self.lineWrite("<identifier> "+currWord+" </identifier>")
        elif(re.match("\".*\"",currWord)):                                              ## String constant
            mString = re.match("\"(.*)\"", currWord);
            if(mString):
                self.lineWrite("<" + "stringConstant" + "> "+mString.group(1)+" </" + "stringConstant" + ">")
        elif(re.match("^([\-|\~])(.*)",currWord)):
            self.lineWrite("<symbol> "+re.match("^([\-|\~])(.*)",currWord).group(1)+" </symbol>")
            self.compileTerm(re.match("^([\-|\~])(.*)",currWord).group(2))
        elif(re.match("(.*)\[(.*)\]", currWord)):
            mSq = re.match("(.*)\[(.*)\]", currWord)
            self.lineWrite("<identifier> " + mSq.group(1) + " </identifier>")
            self.lineWrite("<symbol> [ </symbol>")
            self.compileExpression(mSq.group(2))
            self.lineWrite("<symbol> ] </symbol>")
        elif(re.match("^\((.*)\)", currWord)):
            self.lineWrite("<symbol> ( </symbol>")
            self.compileExpression(re.match("^\((.*)\)", currWord).group(1))
            self.lineWrite("<symbol> ) </symbol>")
        else:
            self.compileSubRoutineCall(currWord)

        self.tab-=1;
        self.lineWrite("</term>")

    def compileExpression(self, currWord):
        currWord = currWord.strip()
        print("in expression", currWord)
        self.lineWrite("<expression>");
        self.tab+=1;


        if(re.match("^\(", currWord)):
            open=1;
            sId=1;
            while(open != 0):
                if(currWord[sId] == '('):
                    open+=1;
                if(currWord[sId] == ')'):
                    open-=1;
                sId+=1;
            newTermWord = currWord[0:sId]
            print("new Word = ", newTermWord)
            self.compileTerm(newTermWord)
            remWord = currWord[sId:].strip();
            if(remWord != ""):
                print("remWord = ", remWord[1:])
                self.lineWrite("<symbol> " +remWord[0] + " </symbol>");
                self.compileTerm(remWord[1:]);
        elif('(' in currWord):
            symMatch = re.match("^([\w|\d]+) ([\+|\-|\*|\/|\&|\||\=|\>|\<]) (\(.*\))$", currWord);
            if(symMatch):
                self.compileTerm(symMatch.group(1));
                self.lineWrite("<symbol> " +symMatch.group(2) + " </symbol>");
                self.compileTerm(symMatch.group(3));
        elif(re.match("^([\w|\d]+) ([\+|\-|\*|\/|\&|\||\=|\>|\<]) ([\w|\d]+)$", currWord)):
            symMatch = re.match("^([\w|\d]+) ([\+|\-|\*|\/|\&|\||\=|\>|\<]) ([\w|\d]+)$", currWord);
            if(symMatch):
                self.compileTerm(symMatch.group(1));
                self.lineWrite("<symbol> " +symMatch.group(2) + " </symbol>");
                self.compileTerm(symMatch.group(3));
        else:
            self.compileTerm(currWord);

        self.tab-=1;
        self.lineWrite("</expression>");
        #self.currLineNum+=1;
        print("out expression")

    def compileWhileStatements():
        print("in While");

        compPtr.write("<whileStatement>");
        compPtr.write("\n");
        compPtr.write("\t");
        tab = tab + 1;
        compPtr.write("<keyword> while </keyword>");
        compPtr.write("<symbol> ( </symbol>");

        compileExpression();

        compPtr.write("<symbol> ) </symbol>");

        compPtr.write("<symbol> { </symbol>");

        compileStatements()

        compPtr.write("<symbol> } </symbol>");

    def __del__(self): 
        print(self.outputFile)
        self.comPtr.close()

    


if __name__ == '__main__':
    
    #tokenizer();
    c = CompilationEngine(jackFilePath);
    c.processFile();
    c.updatePtr();
    while(not c.ifEnd()):
        c.advance();
    del c;
    outPtr.close()
    exit(0)

        





