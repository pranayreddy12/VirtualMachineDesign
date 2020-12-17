

import os;
import sys;
import re;
from os import listdir
from os.path import isfile, join



class Table:
    def __init__(self, name, type, kind, num):
        self.name = name;
        self.type = type;
        self.kind = kind;
        self.num  = num;

class CompilationEngine:

     def __init__(self, filePath):
        self.jackPtr   = open(filePath,"r+").read();
        self.jackLines = self.jackPtr.split('\n');
        self.currLineNum = 0;
        self.tab = 0;
        self.outputFile  = filePath[:-5] + ".vm";
        self.comPtr = open(self.outputFile, "w");
        self.maxLines = 0;
        self.tmpFile  = filePath[:-5] + "tmp" + ".jack1";
        self.tmpPtr = open(self.tmpFile, "w");
        self.className = "";
        self.ifCount=0;
        self.whileCount=0;
        self.classDict = {}
        self.funcDict = {};
        self.funcName = "";
        self.className = "";

     def updatePtr(self):
        self.jackPtr   =open(self.tmpFile, "r+").read();
        self.jackLines = self.jackPtr.split('\n');
        self.maxLines = len(open(self.tmpFile).readlines(  ))

     def lineWrite(self, instring):
        for num in range(self.tab):
            self.comPtr.write("  ");
        self.comPtr.write(instring)
        self.comPtr.write("\n");

     def buildSymbolTable(self):
        jackPtr   = open(self.tmpFile,"r+").read();
        jackLines = jackPtr.split('\n');

        funcName = "";
        className = "";
        for line in jackLines:
            print("line = ", line)
            if("class" in line):
                className = re.match("class (.*) {", line).group(1);
                funcName = "";
                self.classDict[className] = [];
            
            elif(re.match("(function|method|constructor) (\S+) (\S+)\((.*)\).*", line)):
                funMatch = re.match("(function|method|constructor) (\S+) (\S+)\((.*)\).*", line);
                funcName = funMatch.group(3);
                self.funcDict[funcName] = [];
                self.funcDict[funcName].append(Table("this", className, "argument", 0));

                args = funMatch.group(4).strip();
                print("function args = ", args)
                if(',' in args):
                    for idx,arg in enumerate(args.split(',')):
                        arg = arg.strip();
                        type = arg.split(' ')[0];
                        name = arg.split(' ')[1];
                        self.funcDict[funcName].append(Table(name, type, "argument", idx));
                elif (args != ""):
                    type = args.split(' ')[0];
                    name = args.split(' ')[1];
                    self.funcDict[funcName].append(Table(name, type, "argument", 0));

            elif("var" in line):
                if(',' in line):        ## MULTIPLE VARS OF SAME TYPE;
                    varMatch = re.match("var (\S+) (.*);", line);
                    if(varMatch):
                        type = varMatch.group(1);
                        nameArr = varMatch.group(2).strip().split(',');
                        for idx, name in enumerate(nameArr):
                            print("name = ", name)
                            name = name.strip();
                            if(funcName == ""):
                                tabObj = Table(name, type, "local", idx);
                                self.classDict[className].append(tabObj);                            
                            else:
                                tabObj = Table(name, type, "local", idx);
                                self.funcDict[funcName].append(tabObj);
                else:
                    varMatch = re.match("var (.*) (.*);", line);
                    if(varMatch):
                        type = varMatch.group(1);
                        name = varMatch.group(2);
                        if(funcName == ""):     ## CLASS Details.
                            tabObj = Table(name, type, "field", 0);
                            self.classDict[className].append(tabObj);
                        else:                   
                            lastNum = 0;
                            if(len(self.funcDict[funcName]) == 0):
                                print("in lastnum")
                                lastNum = 0;
                            else:
                                lastObj = self.funcDict[funcName][len(self.funcDict[funcName]) - 1]
                                if(lastObj.kind == "local"):
                                    lastNum = lastObj.num + 1;
                            tabObj = Table(name, type, "local", lastNum);
                            self.funcDict[funcName].append(tabObj);

     def printSymbolTable(self):
         for key in self.funcDict:
             print("funcNAme = ", key);
             for obj in self.funcDict[key]:
                 print(obj.name, " ", obj.type, " ", obj.kind, " ", obj.num);

    
     def processComments(self):
        block = 0;
        braOpen = 0;
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
            if(braOpen == 1 and ')' in line):
                newbraLine+=line;
                self.tmpPtr.write(newbraLine);
                self.tmpPtr.write("\n");
                braOpen = 0;
            if('(' in line and ')' not in line):
                newbraLine = line;
                braOpen = 1;
            else:
                self.tmpPtr.write(line);
                self.tmpPtr.write("\n");


        self.tmpPtr.close();

     def advance(self):
         currLine = self.jackLines[self.currLineNum].strip();
         print("curr Line = ", currLine)
         if("class" in currLine and re.match("class (.*) {", currLine)):
             self.compileClass();

         self.currLineNum+=1


     def compileClass(self):
        currLine = self.jackLines[self.currLineNum].strip();

        print("Compiling Class", currLine)

        
        clMatch = re.match("class(.*) {", currLine);

        self.className = clMatch.group(1).strip();

        self.currLineNum+=1;
        currLine = self.jackLines[self.currLineNum].strip();
        
        
        while('static' in currLine or 'field' in currLine):
            self.compileClassVarDec();
            currLine = self.jackLines[self.currLineNum].strip();    

        while('}' not in currLine):
            self.compileSubRoutineDec();
            currLine = self.jackLines[self.currLineNum].strip();
        
        print("className =",self.className);
        

     def compileClassVarDec(self):
        print("in class var dec")
        currLine = self.jackLines[self.currLineNum].strip();
        mClass = re.match("^(\S+) (\S+) (.*);", currLine)

        if(mClass):
            classField = mClass.group(1);
            classType  = mClass.group(2);
            #classVarName_Type = self.compileVars(mClass.group(3)).split(' ');
            #print(classVarName_Type)
            #for varName in classVarName_Type:
            #    self.classVarTable[varName] = VarTable(classField, classType);

        self.currLineNum+=1; 

     def compileSubRoutineDec(self):
        currLine = self.jackLines[self.currLineNum].strip();
        print(" in subroutine dec method .. ", currLine);
        mRotMatch = re.match("^(function|method|constructor) (\S+) (\S+)\((.*)\).*", currLine)
        retType = "";
        funName = "";
        args    = "";
        if(mRotMatch):
            subType = mRotMatch.group(1).strip();
            retType = mRotMatch.group(2).strip();
            funName = mRotMatch.group(3).strip();
            args    = mRotMatch.group(4).strip();
            print("fun name =", (funName))
            self.funcName = funName;
            count = 0;

            print("dict = ", self.funcDict[funName]);
            
            for key in self.funcDict[funName]:
                #print(key);
                #print(self.funcDict[funName][key])
                if(key.kind != "argument"):
                    count+=1;

            self.lineWrite("function "+ self.className+"."+funName + " "+ str(count))

            self.compileSubRoutineBody();



     def compileSubRoutineBody(self):
        print(" in sub routine body");
#        self.lineWrite("<subroutineBody>")
#        self.tab+=1;
#        self.lineWrite("<symbol> { </symbol>")

        self.currLineNum+=1;

        currLine = self.jackLines[self.currLineNum].strip();

       
        while('var' in currLine):
            self.compileVarDec(currLine)
            self.currLineNum+=1
            currLine = self.jackLines[self.currLineNum].strip();
        
        self.compileStatements();
        
        #self.lineWrite("<symbol> } </symbol>")
        self.currLineNum+=1;
        #self.tab-=1;
        #self.lineWrite("</subroutineBody>")
        print(" out of sub routine body")


     def compileVarDec(self, currLine):
        print(" in var dec");
        vMatch = re.match("var (\S+) (.*);", currLine);

        if(vMatch):
            #self.lineWrite("<varDec>")
            #self.tab+=1;
            #self.lineWrite("<keyword> var </keyword>")
            
            type = vMatch.group(1);
            self.compileVars(vMatch.group(2), type);
            #self.lineWrite("<symbol> ; </symbol>")
            #self.tab-=1;
            #self.lineWrite("</varDec>")   

     def compileVars(self, currWord, type):
        currWord = currWord.strip();
        varMatch = re.match("([^,]+)\,([^,]+)", currWord)
        if(varMatch):
            #self.lineWrite("<identifier> " + varMatch.group(1) + " </identifier>")
            #self.lineWrite("<symbol> , </symbol>")
            self.compileVars(varMatch.group(2), type)
        else:
            #self.funcTable[currWord] = VarTable("local", type);
            pass
            #self.lineWrite("<identifier> " + currWord + " </identifier>")

     def compileStatements(self):
        print("In general statement");
        currLine = self.jackLines[self.currLineNum].strip();

        #self.lineWrite("<statements>")
        #self.tab+=1;

        while(currLine[0].strip() != '}'):
            self.compileStatement(currLine);
            self.currLineNum+=1;
            currLine = self.jackLines[self.currLineNum].strip();

        #self.tab-=1;
        #self.lineWrite("</statements>")
        print("out of general statement");

     def compileStatement(self, currLine):
        print("in compile statement low", currLine);
        currLine = currLine.strip();
        
        if(currLine.startswith('let')):
            self.compileLetStatement(currLine);
        elif(currLine.startswith('do')):
            self.compileDoStatement(currLine);
        elif(currLine.startswith('if')):
            self.compileIfStatement();
        elif(currLine.startswith('while')):
            self.compileWhileStatements();
        elif(currLine.startswith('var')):
            self.compileVarDec(currLine)
        elif(currLine.startswith('return')):
            self.compileReturn(currLine)
         
     def compileLetStatement(self, currLine):
        print("in Let");

        lMatch = re.match("let (\S+) = (.*);", currLine);
        if(lMatch):
            if(re.match("let (.*)\[(.*)\] =.*", currLine)):
                mSq = re.match("let (.*)\[(.*)\] =.*", currLine)
                self.compileExpression(mSq.group(2))
            else:
                print("");
            
            self.compileExpression(lMatch.group(2));

            leftVar = lMatch.group(1);

            for key in self.funcDict[self.funcName]:
                if(key.name == leftVar):
                    self.lineWrite("pop " + key.kind + " " + str(key.num))
                    break;
            

     def compileWhileStatements(self):
        print("in While");
        self.lineWrite("label WHILE_EXP" + str(self.whileCount));
        currLine = self.jackLines[self.currLineNum].strip();
        wMatch = re.match("while \((.*)\) {", currLine)
        if(wMatch):
            self.compileExpression(wMatch.group(1));
            self.lineWrite("not")
            self.lineWrite("if-goto WHILE_END" + str(self.whileCount));
            self.whileCount+=1;
            self.currLineNum+=1;
            self.compileStatements();
        self.whileCount-=1;
        self.lineWrite("goto WHILE_EXP" + str(self.whileCount));
        self.lineWrite("label WHILE_END" + str(self.whileCount));


     def compileIfStatement(self):
        print("in IF");
        currLine = self.jackLines[self.currLineNum].strip();

        ifMatch = re.match("if \((.*)\).*{",currLine )
        if(ifMatch):            
            self.compileExpression(ifMatch.group(1));
            self.lineWrite("if-goto IF_TRUE" + str(self.ifCount))
            self.ifCount+=1;
            self.lineWrite("goto IF_FALSE" + str(self.ifCount-1));
            self.lineWrite("label IF_TRUE"+str(self.ifCount-1));

            if2Match = re.match("if \((.*)\).*{(.*)}",currLine )
            if(if2Match):
                self.compileStatement(if2Match.group(2));
            else:
                self.currLineNum+=1;
                self.compileStatements();

            self.lineWrite("goto IF_END" + str(self.ifCount-1));
            print(" INNN IFF",self.jackLines[self.currLineNum+1].strip())
            if('else' in self.jackLines[self.currLineNum+1].strip()):
                self.lineWrite("label IF_FALSE"+str(self.ifCount-1));    
                self.currLineNum+=1;
            
                self.currLineNum+=1;
                self.compileStatements();
            self.lineWrite("label IF_END" + str(self.ifCount-1));
            self.ifCount-=1;
           
        print("Out of IF");


     def compileDoStatement(self, currLine):
        print(" in do function");
        #self.lineWrite("<doStatement>")
        #self.tab+=1;
        #self.lineWrite("<keyword> do </keyword>")
        doMatch = re.match("do (.*);", currLine);
        if(doMatch):
            self.compileSubRoutineCall(doMatch.group(1))
        self.lineWrite("pop temp 0")
        #self.lineWrite("<symbol> ; </symbol>")
        #self.tab-=1;
        #self.lineWrite("</doStatement>")


     def compileSubRoutineCall(self, currWord):
        print("in sub routine call", currWord)
        currWord = currWord.strip()
        
        if('.' not in currWord):                    ### FUNC(exp1, exp2, ...)
            id = 0;
            while(currWord[id] != '('):
                id+=1;

            subName = currWord[:id];
            expList = currWord[id+1:len(currWord) - 1];
            #self.compileSubRoutineName(subName);
            #self.lineWrite("<symbol> ( </symbol>")
            self.compileExpressionList(expList);
            self.lineWrite("call " + subName);
            self.lineWrite("pop temp 0");

            #self.lineWrite("<symbol> ) </symbol>")
            #print("subName = ", subName)
            #print("expList = ", expList)
        else:
            id1 = 0;
            while(currWord[id1] != '.'):
                id1+=1;

            id2 = 0;
            while(currWord[id2] != '('):
                id2+=1;
            print("id1 = ", id1, "id2 = ", id2)
            className = currWord[:id1];
            subName = currWord[id1+1:id2];
            expList = currWord[id2+1:len(currWord) - 1] ;
            print("className = ", className)
            print("subName = ", subName)
            print("expList = ", expList)


            #self.compileVarName(className);
            #self.lineWrite("<symbol> . </symbol>")
            #self.compileSubRoutineName(subName);
            #self.lineWrite("<symbol> ( </symbol>")
            self.compileExpressionList(expList);
            
            self.lineWrite("call "+ className+ "."+ subName + " " + str(len(expList.split(','))))
            #self.lineWrite("pop temp 0")
            #self.lineWrite("<symbol> ) </symbol>") 

     def compileExpressionList(self, currWord):
        #self.lineWrite("<expressionList>")
        #self.tab+=1;
        print(" in expression list function");
        expWords = currWord.split(',');
        expCount = 0;
        
        for word in expWords:
            expCount+=1;
            if(word.strip()==""):
                break;
            print("calling ... ", word)
            self.compileExpression(word);
            if(expCount == len(expWords)):
                break;
            #self.lineWrite("<symbol> , </symbol>")

        #self.tab-=1;
        #self.lineWrite("</expressionList>")

     def compileExpression(self, currWord):
        currWord = currWord.strip()
        print("in expression", currWord)
        #self.lineWrite("<expression>");
        #self.tab+=1;


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
            remWord = currWord[sId:];
            remWord = remWord.strip();
            if(remWord != ""):
                    self.compileTerm(remWord[1:]);
                    print("remWord = ", remWord)
                    if 1:
                        if(remWord[0].strip() == '<'):
                            self.lineWrite("<symbol> &lt; </symbol>");
                        elif(remWord[0].strip() == '>'):
                            print(" got the >")
                            self.lineWrite("<symbol> &gt; </symbol>");
                        elif(remWord[0].strip() == '&'):
                            self.lineWrite("<symbol> &amp; </symbol>");
                        elif(remWord[0].strip() == '='):
                            self.lineWrite("eq");
                            #self.lineWrite("<symbol> " +remWord[0] + " </symbol>");
        
        elif(re.match("^([\w|\d]+) ([\+|\-|\*|\/|\&|\||\=|\>|\<]) (\(.*\))$", currWord)):               ## EXP OP EXP
            symMatch = re.match("^([\w|\d]+) ([\+|\-|\*|\/|\&|\||\=|\>|\<]) (\(.*\))$", currWord);
            if(symMatch):
                print(" IN COMPILE TERM1 , ..... .. ", symMatch.group(2))
                
                ## EXP1
                self.compileTerm(symMatch.group(1));
                ## EXP2
                self.compileTerm(symMatch.group(3));

                ### OP
                op = symMatch.group(2);
                if(op == '<'):
                    self.lineWrite("lt");
                elif(op == '>'):
                    print(" got the >")
                    self.lineWrite("gt");
                elif(op == '&'):
                    self.lineWrite("and");
                elif(op == '+'):
                    self.lineWrite("add");
                elif(op == '-'):
                    self.lineWrite("sub");
                elif(op == '*'):
                    self.lineWrite("call Math.multiply 2");
                elif(op == '='):
                    self.lineWrite("eq");
                else:
                    sel.lineWrite(op)
                
        elif(re.match("^([\-|\~])(.*)",currWord)):                                                                  ## OP TERM. 
        #    self.lineWrite("<symbol> "+re.match("^([\-|\~])(.*)",currWord).group(1)+" </symbol>")
            self.compileTerm(re.match("^([\-|\~])(.*)",currWord).group(2))
            if('~' in currWord):
                self.lineWrite("not")
            else:
                self.lineWrite("neg")
            
        elif(re.match("^(.*) ([\+|\-|\*|\/|\&|\||\=|\>|\<]) (.*)$", currWord)):
            symMatch = re.match("^(.*) ([\+|\-|\*|\/|\&|\||\=|\>|\<]) (.*)$", currWord);
            if(symMatch):
                print(" IN COMPILE TERM2 , ..... .. ", symMatch.group(2))
                self.compileTerm(symMatch.group(1));
                self.compileTerm(symMatch.group(3));
                op = symMatch.group(2);
                if(op == '<'):
                    self.lineWrite("lt");
                elif(op == '>'):
                    print(" got the >")
                    self.lineWrite("gt");
                elif(op == '&'):
                    self.lineWrite("and");
                elif(op == '+'):
                    self.lineWrite("add");
                elif(op == '-'):
                    self.lineWrite("sub");
                elif(op == '*'):
                    self.lineWrite("call Math.multiply 2");
                elif(op == '='):
                    self.lineWrite("eq");
                else:
                    self.lineWrite(op)

        else:
            self.compileTerm(currWord);

        #self.tab-=1;
        #self.lineWrite("</expression>");
        #self.currLineNum+=1;
        print("out expression")

     def compileTerm(self, currWord):
        currWord = currWord.strip();
        print("in term", currWord)
        #self.lineWrite("<term>")
        #self.tab+=1;
        #re.match();
        
        if(re.match("^[\d]+$", currWord)):                                                                          ## DECIMAL
            self.lineWrite("push constant " + currWord);
            #self.lineWrite("<integerConstant> "+currWord+" </integerConstant>")
        elif(currWord in ['true', 'false', 'null', 'this']):
            if(currWord == 'true'):
                self.lineWrite("push constant 0")
                self.lineWrite("not")
            elif(currWord == 'false'):
                self.lineWrite("push constant 0")
        elif(re.match("^[\w]+$",currWord)):                                                                         ## Key word constant
            print(" finding for mask ,, debug")
            for key in self.funcDict[self.funcName]:
                if(key.name == currWord):
                    self.lineWrite("push " + key.kind + " " + str(key.num));
                    break;
            

            #self.lineWrite("push var " + currWord);
         #   self.lineWrite("<identifier> "+currWord+" </identifier>")
        elif(re.match("\".*\"",currWord)):                                                                          ## String constant
            self.lineWrite("push constant " + currWord);
         #   mString = re.match("\"(.*)\"", currWord);
          #  if(mString):
           #     self.lineWrite("<" + "stringConstant" + "> "+mString.group(1)+" </" + "stringConstant" + ">")
        elif(re.match("^([\-|\~])(.*)",currWord)):                                                                  ## OP TERM. 
        #    self.lineWrite("<symbol> "+re.match("^([\-|\~])(.*)",currWord).group(1)+" </symbol>")
            self.compileTerm(re.match("^([\-|\~])(.*)",currWord).group(2))
            if('~' in currWord):
                self.lineWrite("not")
            else:
                self.lineWrite("neg")
        elif(re.match("(.*)\[(.*)\]", currWord)):                                                                   ## ARRAY RELATED
            mSq = re.match("(.*)\[(.*)\]", currWord)
        #    self.lineWrite("<identifier> " + mSq.group(1) + " </identifier>")
         #   self.lineWrite("<symbol> [ </symbol>")
            self.compileExpression(mSq.group(2))
          #  self.lineWrite("<symbol> ] </symbol>")
        elif(re.match("^\((.*)\)", currWord)):                                                                      ## (expression)
           # self.lineWrite("<symbol> ( </symbol>")
            self.compileExpression(re.match("^\((.*)\)", currWord).group(1))
            #self.lineWrite("<symbol> ) </symbol>")
        else:
            self.compileSubRoutineCall(currWord)

        #self.tab-=1;
        #self.lineWrite("</term>")
        print("end of term", currWord)

     def compileReturn(self, word):
         print("In return function")
         if(re.match("return;", word)):
             self.lineWrite("push constant 0");
             self.lineWrite("return")
         else:
            retMatch = re.match("return (.*);", word);
            if(retMatch):
                self.compileExpression(retMatch.group(1));
                self.lineWrite("return")


     def ifEnd(self):
        if(self.currLineNum == len(self.jackLines)):
            return True;
        else:
            return False;



if __name__ == '__main__':

    print("starting script")
    inPath = sys.argv[1]
    print("inPath = ", inPath)

    if(os.path.isdir(inPath)):
        onlyfiles = [f for f in listdir(inPath) if isfile(join(inPath, f))]
        for file in onlyfiles:
            if(not file.endswith("jack")):
                continue;
            file = inPath + "/"+ file;
            print("file =", file)
            c = CompilationEngine(file);
            c.processComments();
            c.buildSymbolTable();
            c.printSymbolTable();
            c.updatePtr();
            while(not c.ifEnd()):
                c.advance();
            del c;
    else:
        c = CompilationEngine(inPath);
        c.processComments();
        c.updatePtr();
        while(not c.ifEnd()):
            c.advance();
        del c;



