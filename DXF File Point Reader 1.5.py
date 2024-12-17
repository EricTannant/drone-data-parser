import re

xcoord = "x"
ycoord = "y"
zcoord = "z"

linenum = 0
pattern = re.compile("POINT")

filename = input("Enter the file name: ")
fh = open('result.txt', 'a')
with open(filename, 'r+') as file:
    fh.write("Start of coords for file: " + filename + "\n")
    fh.write("\n")
    for myline in file:
        linenum += 1

        if pattern.search(myline) != None:
            i = 0
            while i < 12:
                myline = file.readline()
                i += 1

            # print(myline)
            xcoord = myline
            myline = file.readline()
            myline = file.readline()
            # print(myline)
            ycoord = myline
            myline = file.readline()
            myline = file.readline()
            # print(myline)
            zcoord = myline
            # print(xcoord.rstrip("\n") + ", " + ycoord.rstrip("\n") + ", " + zcoord)
            # fh.write(xcoord.rstrip("\n") + "\t" + ycoord.rstrip("\n") + "\t" + zcoord.rstrip("\n") + "\n")
            fh.write(xcoord.rstrip("\n") + ", " + ycoord.rstrip("\n") + ", " + zcoord.rstrip(", ") + "\n")


fh.write("End of coords for file: " + filename + "\n")
fh.write("\n")
fh.close()