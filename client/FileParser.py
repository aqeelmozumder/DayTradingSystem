
Usernames = []
userlists = {}
logcommand = []

def Parser():

    with open("./client/Commands.txt", "r") as file:
            count = 1
            Input : list
            for lines in file:
                # Input = []
                #This is to remove the enumeration in the file which is included with the Squrare brackets, like remove [1],[2] and so on
                RemoveCharacters = "[" + str(count) + "]"

                #Will strip [1],[2] etc. will also remove whitespaces and trailing new lines. Then split them between the commas
                Input = lines.strip(RemoveCharacters).strip(" ").rstrip("\n").rstrip(" ").split(",")
            # print(Input)
                

                if(Input[0] != "DUMPLOG"):
                    # print('hello')
                    # print(Input
                    if(len(Usernames) == 0):
                        name = str(Input[1])+"List" 
                        userlists[name] = []
                        userlists[name].append(Input)
                        Usernames.append(Input[1])            
                    else:

                        
                        if(Input[1] in Usernames):
                            userlists[str(Input[1])+"List"].append(Input)
                        else:
                            name = str(Input[1])+"List" 
                            userlists[name] = []
                            userlists[name].append(Input)
                            Usernames.append(Input[1])
                            # print(userlists[name])          

                else:
                    if(len(Input) == 3):
                        if(Input[1] in Usernames):
                            userlists[str(Input[1])+"List"].append(Input)
                        else:
                            name = str(Input[1])+"List" 
                            userlists[name] = []
                            userlists[name].append(Input)
                            Usernames.append(Input[1])            

                    elif(len(Input) == 2):
                        # Name = Usernames[len(Usernames)-1]
                        # userlists[Name+"List"].append(Input)
                        logcommand.append(Input)
                count = count +1


    res = [[i for i in userlists[x]] for x in userlists.keys()]
    return res


def log():
    return logcommand