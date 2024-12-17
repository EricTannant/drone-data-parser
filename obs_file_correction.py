# Code corrects all .obs files in the same folder. Just run the code within the folder to convert all of them at once.
 
import os
import math

# finds files with .obs file extensions
filename = [f for f in os.listdir(os.getcwd()) if os.path.splitext(f)[-1]=='.obs'] 

newfilename = []

# loop over all the files
for i in range(len(filename)):
    newfilename.append(filename[i].split('.')[0]+'_corrected'+'.txt' )   # name of the corrected file
    flag = 0        # this ensure only the first time instance is removed
    lines = []      # line array

    file =  open(filename[i], 'r+')     # opens file in read and write mode
    new = open(newfilename[i],'w')      # opens file in just write mode

    #loop through the file reading each line
    while True:
        line = file.readline()      # reads line one by one
        if not line:                # if no line, it comes out of the loop and ends  
            break
        if(line[0] == '>'):         # finds the first >
            flag+=1
            ll = line.split(None)
            # time instance with required number of spaces
            # current format 
            # >.x..x.x.x.x..x..x.x where '.' are the spaces
            if len(ll[2]) == 1:
                ll[2] = ' '+ll[2]
            if len(ll[3]) == 1:
                ll[3] = ' '+ll[3]
            if len(ll[4]) == 1:
                ll[4] = ' '+ll[4]
            if len(ll[5]) == 1:
                ll[5] = ' '+ll[5]
            if ll[6][1]=='.':
                ll[6]=' '+ll[6]
            if len(ll[7]) == 1:
                ll[7] = ' '+ll[7]
            if len(ll[8]) == 1:
                ll[8] = ' '+ll[8]
                
            line = '> '+ ll[1] +' ' +  ll[2] +' '+ll[3]+' '+ll[4]+' '+ll[5]+' '+ll[6]+' '+ll[7]+' '+ll[8]+'\n'       
        if(flag == 1 ):              # ignores if it's not the first >
            continue
        if(line[0] == '>' and flag == 2):
            store = line            # store the time corresponding to the second > for further processing in the file
        new.write(line)             # writes the line to other file
    
    # splits the time instance into a list     
    l = store.split(None)
    l2 = store.split(None)
    
    if len(l[2]) == 1:
        l[2] = ' '+l[2]
    if len(l[3]) == 1:
        l[3] = ' '+l[3]
    if len(l[4]) == 1:
        l[4] = ' '+l[4]
    if len(l[5]) == 1:
        l[5] = ' '+l[5]
    if l[6][1]=='.':
        l[6]=' '+l[6]
    str2 = '  ' + l[1] +'    ' +  l[2] +'    '+l[3]+'    '+l[4]+'    '+l[5]+'   '+l[6]+'     GPS         TIME OF FIRST OBS\n'   # some line customization as it fits according to the obs file    

    # add 0 in front of the month, day, hour, minute, second on line 2 if any of these is a single digit
    if len(l2[2]) == 1:
        l2[2] = '0'+l2[2]
    if len(l2[3]) == 1:
        l2[3] = '0'+l2[3]
    if len(l2[4]) == 1:
        l2[4] = '0'+l2[4]
    if len(l[5]) == 1:
        l2[5] = '0'+l2[5]
    l2[6] = str(math.floor(float(l2[6])))
    if len(l2[6]) == 1:
        l2[6] = '0'+l2[6]
    str1 = 'RTKCONV 2.4.3 b29                       '+l2[1]+l2[2]+l2[3]+' '+l2[4]+l2[5]+l2[6]+' UTC PGM / RUN BY / DATE\n' # some more line customizations
    new.close()

    new = open(newfilename[i],'r+')         
    tnew = open('tnew.txt','w')
    find1 = 'UTC PGM / RUN BY'          # replaces the lines wherever these words are written
    find2 = 'TIME OF FIRST OBS'         # replaces the lines wherever these words are written
    find3 = 'END OF RINEX OBS DATA'     # this is the last line
    intervalstr = "                                                            0.2000 INTERVAL     \n"

    # the code replaces the time lines and removes the last line
    while True:
        #parses full file
        line = new.readline()
        if not line:
            break

        if not line.isspace():
            if find3 in line:
                break
            elif find1 in line:
                tnew.write(str1)
            elif find2 in line:
                tnew.write(intervalstr)
                tnew.write(str2)
            else:
                tnew.write(line)
                
    tnew.write(' ') # adds a space at the end of the line
    new.close()
    tnew.close()
    os.remove(newfilename[i])
    os.rename('tnew.txt',newfilename[i]) # replaces the temp file name with the new file
    # print(filename[i]+'Corrected')        

# print('All obs files are corrected and can be found in the same folder with \'_corrected\' in the filename!')