#!/usr/bin/python

##################
# Custom Exam Generator for iClicker classrooms
# by Benjamin Monreal (CC BY 4.0) 2014   bmonreal@physics.ucsb.edu
# Released under Creative Commons, Attribution 4.0 International license.
# Feel free to modify, reuse, personalize, publish, or commercialize 
# this code as long as my name remains attached to it and its derivatives.
##################

import csv
import sys
import random
import getopt


from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

from PyPDF2 import PdfFileWriter, PdfFileReader



import Tkinter, tkFileDialog, tkSimpleDialog
from Tkinter import *
from PIL import Image
from os import listdir, remove
from os.path import isfile, join, getsize

class MyDialog(tkSimpleDialog.Dialog):

    def body(self, master):

        Label(master, text="Number of questions per student:", default="4").grid(row=0)
        Label(master, text="Page layout? (ignore this)").grid(row=1)
        Label(master, text="Page layout? (ignore this):").grid(row=2)
        self.e1 = Entry(master)
        self.e2 = Entry(master)
        self.e3 = Entry(master)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)

        var1 = IntVar()
        var2 = IntVar()
#        self.cb1 = Checkbutton(master, text="Presenter display?",variable=var1)
        self.cb1 = Checkbutton(master, text="This button doesn't work",variable=var1)
        self.cb1.grid(row=4, columnspan=2, sticky=W)
#        self.cb2 = Checkbutton(master, text="Show left side of screen?",variable=var2)
        self.cb2 = Checkbutton(master, text="This button doesn't work either",variable=var2)
        self.cb2.grid(row=5, columnspan=2, sticky=W)

        return self.e1 # initial focus

    def apply(self):
        self.result = int(self.e1.get()),  int(self.e2.get()),  int(self.e3.get())

mypath=""
examsdir=""
prefixpdfname=""
postfixpdfname=""
rosterfilename=""
#nneeded = 6 # this is now set in the user-specific part above
layout = [2,3] 
fullscreen = False
cropleft = False
IgnoreSkippedQuestions = True
nameonbackpage = True
        
root = Tk()
root.update()

#########################################
##### get user input ####################
try:
    # see if there's a command-line argument
    opts, args = getopt.getopt(sys.argv[1:],"c:o:f:l:n:ks",["class=","output=","prefix=","postfix=","fullscreen","cropleft"])

except getopt.GetoptError:
    print "Run parse_students with no arguments to get interactive prompts."
    print "or run (all args required)"
    print "parse_students -c <clicker class directory> -o <exam directory> -f <pdf file to prefix> -l <pdf file to postfix> -n <number of questions per student>"
    
print opts
print args

for opt, arg in opts:
    # if it's a command-line invocation, parse arguments for input parameters and text-prompt for missing ones.
    if opt in ("-c","--class"):
        print "entering opt loop"
        mypath = arg
    elif opt in ("-o","--output"):
        examsdir = arg
    elif opt in ("-f","--prefix"):
        prefixpdfname = arg
    elif opt in ("-l","--postfix"):
        postfixpdfname = arg
    elif opt in ("-n"):
        nneeded = int(arg)
    elif opt in ("-s"):
        fullscreen = True
    elif opt in ("-k"):
        cropleft = True

whoseclass = "JC"
if (whoseclass=="JC"):

    mypath = "/Users/bmonreal/Desktop/iclicker_Mac_v6.4.2_ucsbintegration_2014-10-24/Classes/Physics 20 Fall 2015/"
    examsdir = "/Users/bmonreal/software/ClickerExamMaker/Midterms_phys20f15jc/"
    rosterfilename = "/Users/bmonreal/Desktop/iclicker_Mac_v6.4.2_ucsbintegration_2014-10-24/Classes/Physics 20 Fall 2015/MoodleRoster.txt"
    nneeded = 5
    firstnumber = 11
if (whoseclass=="BM"):
    mypath = "/Users/bmonreal/Desktop/iclicker_Mac_v6.4.2_ucsbintegration_2014-10-24/Classes/Phys20F15_Monreal/"
    examsdir = "/Users/bmonreal/software/ClickerExamMaker/Midterms_phys20f15bm/"
    rosterfilename = "/Users/bmonreal/Desktop/iclicker_Mac_v6.4.2_ucsbintegration_2014-10-24/Classes/Phys20F15_Monreal/MoodleRoster.txt"
    nneeded=6
    firstnumber = 1
#postfixpdfname = "/Users/bmonreal/teaching/phys21w14/final_exam.pdf"
postfixpdfname = ""
prefixpdfname=""
print "hack line select "+mypath+" "+examsdir

# hand-coded arrays that generate the list of seats in this classroom.  
whichclassroom = "1640"
listofseats = []
alternatingseats = []
if (whichclassroom=="1640"):
    listofseats += ["J"+str(x) for x in range(104,110+1)] #short row
    listofseats += ["H"+str(x) for x in range(105,110+1)] #short row
    for rowletter in ["G","F","E","D","C"]:
        listofseats += [rowletter+str(x) for x in range(101,111+1)] # five uniform rows
    listofseats += ["B"+str(x) for x in range(101,110+1)]  # one seat short in row B
    listofseats += ["A101"] # front rows are half broke, only use a few
    listofseats += ["A102"]
    listofseats += ["A110"]
alternatingseats += ['A' if pow(-1,i)==1 else "B" for i in range(len(listofseats))]

print "seat list length ", len(listofseats)
print "seat alt length ", len(alternatingseats)
print listofseats

# if there were NO command line arguments, we have to prompt for the number and layout of the questions.          
#if len(opts) == 0 :
#    d = MyDialog(root)
##    userinput = d.result
#    nneeded = userinput[0]
#    layout = [userinput[1],userinput[2]]

# FIXME: I don't know how to implement these radio buttons.  
#    fullscreen = userinput[3];
#    cropleft = userinput[4];
fullscreen = True
cropleft = False

# All of the filenames are required; prompt for anything missing.
# FIXME: would be better to tie "prefix" and "postfix" files to an option
# so it's easier to skip them if you don't want them.
print 'Entering interactive mode.'
if mypath=="":
    mypath = tkFileDialog.askdirectory(title="Please select the iClicker folder for this class.")+"/"
if examsdir=="":    
    examsdir = tkFileDialog.askdirectory(title="Please select a folder in which to save the exams")+"/"
if rosterfilename=="":
    rosterfilename = tkFileDialog.askopenfilename(title="Please find the class roster in Moodle format.")
#if prefixpdfname=="":
#    prefixpdfname = tkFileDialog.askopenfilename(title="Please select PDF file you want prepended to every exam.  (Cancel if none.)")
#if postfixpdfname=="":    
#    postfixpdfname = tkFileDialog.askopenfilename(title="Please select PDF file you want post-pended to every exam. (Cancel if none.)")


#################### 
# Key to grading:
# Z = Malfunctioning question, inhibit from exam generation
# AZ, BZ, CZ, DZ, EZ = inhibit from exam use BUT maybe use for gradebook

################ Input student information #################
# Step 1.   The "RemoteID.csv" file helps create a map from clickerIDs to emails
# and the "moodleroster.txt" (exported from iGrader) maps from emails to names. #  Not the best system but we can handle it.  

idfile = open(mypath+"/SessionData/RemoteID.csv",'rU');
idreader = csv.reader(idfile)
students = {}
studentids = {}
for row in idreader:
    if len(row[0])==9: # check for a common invalid-clicker-ID error
        students[row[0]] = {}
        studentids[row[0]] = row[1]  #key is clicker-ID, value is email
        print row[0], row[1]
idfile.close();

emaildb = {}
idfile = open(rosterfilename);
idreader = csv.reader(idfile,delimiter='\t')
idreader.next(); #skip first line
for row in idreader:
    print "roster = ", row
    firstname = row[0]
    lastname = row[1]
    email = row[2]
    emaildb[email] = lastname + ", " + firstname;
emaildb['missing'] = "unregistered, unregistered"


################ Read all clicker/class session information #############
# the goal of this read is to 
# (a) open each session file & learn the "correct" answers from the 6th row
# (b) go down the each students and add each question as a "T/F" (right wrong) to the student's answer dictionary 
# (c) accumulate a list of question-IDs to help find the question images later.

qfiles = {}
correctanswersbyq = {}

files = [ f for f in listdir(mypath+"SessionData/") if ( isfile(mypath+"SessionData/"+f) and "L" in f and "csv" in f and f[0] != 'x')]
# begin loop through list of files!   
for f in files:
    print(f)
    if (getsize(mypath+"SessionData/"+f)==0):
        continue

    csvfile = open(mypath+"SessionData/"+f,'rU')
    thisfile = csv.reader(csvfile)
    i=0;
    # read 2nd row, count questions
    row = thisfile.next()
    row = thisfile.next()
    numquestions = row.count(" Score");
    print(numquestions)
    # get list of correct answers and generate keys for each q
    while (row[0] != "Correct Answer"):
        row = thisfile.next()
    correctanswer = []
    qkey = []
    for i in range (0,numquestions):
        correctanswer.append(row[3+6*i]);
        qkey.append(f[0:len(f)-4]+".q"+str(i+1)); #FIXME need to add question ID to qkey
        print correctanswer[i],qkey[i];
        
        # generate image file name for this question
        thisqimage = mypath+"Images/"+f[0:len(f)-4]+"_Q"+str(i+1)+".jpg";
        # if image file does not exist, kill question by replacing answer with Z
        print thisqimage;
        qfiles[qkey[i]] = thisqimage;
        correctanswersbyq[qkey[i]] = correctanswer[i]
        if not (isfile(thisqimage)):
            print "killit, no file"
            correctanswer[i] = "Z"
        if (correctanswer[i] == ''): # iGrader uses "blank answer" to delete Qs
            print "killit, answer blank single quotes"
            correctanswer[i] = "Z"
        if (correctanswer[i] == ""): # iGrader uses "blank answer" to delete Qs
            print "killit, answer blank double quotes"
            correctanswer[i] = "Z"
        if not ('A' in correctanswer[i] or 'B' in correctanswer[i] or 'C' in correctanswer[i] or 'D' in correctanswer[i] or 'E' in correctanswer[i]):
            print "killit, answer not in set ABCDE"
            correctanswer[i] = "Z"
            
    print "correct answers today are ", correctanswer    
    # OK, now I know the number of questions and the correct answers.  Time to go through the remaining rows and populate the "student answers" database.
    for row in thisfile:
        # see if this student clicker is in the dictionary already
        thisstudent = row[0]
        if thisstudent[0] != '#': # test whether this row of the database looks like a clicker ID. Ugly HACK HACK.
            continue
        if thisstudent not in students:
            print "new student", thisstudent, row
            students[thisstudent] = {}
            studentids[thisstudent] = 'missing'
        # get this student record in hand and prepare to add values to it    
        thisstudentrecord = students[thisstudent];
        # add to database one question at a time
        for i in range (0,numquestions):            
            thisanswer = row[3+6*i]
            # edge case processing
            result = False
            if (IgnoreSkippedQuestions and thisanswer==""):
                result = True
            if (correctanswer[i] == "" and thisanswer==""):
                result = True
            elif (thisanswer!="" and thisanswer in correctanswer[i]):
                result = True;

#            thisstudentrecord[qkey[i]] = result;
#            print f,i,thisstudent,thisanswer,correctanswer[i],result;
             
            if ('Z' in correctanswer[i]): # skip the database entry if "answer Z" indicates a problem with the question or a desire not to use it in exam 
                continue;

            thisstudentrecord[qkey[i]] = result; # add new q-records to student
        students[thisstudent] = thisstudentrecord # refile whole set of student q-records with student 
    csvfile.close();

######### done with input, begin output ##############
# At this point in the code we have:
# --dictionary "students".  Keys are clickerID, datafield is a "student record"
# --student records (stored in "students").  keys are questionIDs, datafield is T/F (right/wrong)
# --dictionary "qfiles", paths to images in clicker image directory
# --student clickerid-to-email dictionary "studentids"
# --student email-to-realname database (roster)
###################################

# Step 2.  Preprocess question image files.
print "preparing to crop"
listofquestions = qfiles.keys();
for thisqkey in listofquestions:
    thisfile = qfiles[thisqkey]
    print "cropping",thisfile,thisqkey," with instructions ",fullscreen,cropleft
    im = Image.open(thisfile)
    
    # DECIDE ON THE CROPPING HERE                               
    if (fullscreen and not cropleft):         
        im = im.crop([1,1,1024,768])
    elif (fullscreen and cropleft):
        im = im.crop([1,1,512,768])
    elif (not fullscreen and not cropleft):
#        im = im.crop([45,125,535,572])
        im = im.crop([104,159,472,480])
    elif (not fullscreen and cropleft):                   
        print "cropping properly now dammit"
        im = im.crop([45,125,290,550])

    # generate a new filename to save the crop
    newfilename = examsdir+"/"+thisqkey+"_crop.jpg";
    im.save(newfilename,"JPEG")
    #replace old qkey filename with this filename
    qfiles[thisqkey] = newfilename

# Step 3.  Go through list of student and generate exams
#

try:
    prefixpages = PdfFileReader(file(prefixpdfname, "rb"))
except:
    prefixpages = ""

try: 
    postfixpages = PdfFileReader(file(postfixpdfname, "rb"))
except:
    postfixpages = ""


# Prepare a file for hte answer key
answerkeyfile = open(examsdir+"/answers.csv","w")
    
listofstudents = students.keys(); # NOTE if we use students.keys for roster, we get only Moodle-registered students.
# it is possible for people to appear in RosterID.csv who are not Moodle registered, I think.
    
istudent = 0
print "student list length ",len(listofstudents)
print listofstudents

for individual in listofstudents:
    istudent += 1
    
    thisrecord = students[individual]
    thisemail = studentids[individual]
    thisname = emaildb[thisemail]
    thisnameforfile = thisname.replace(',','_').replace(' ','_').replace('__','_')
    outputpdfname = examsdir+"/exam"+thisnameforfile+".pdf"
    c = canvas.Canvas(outputpdfname+"tmp",pagesize=letter)
######
# generate a cover page with a seat assignment 
#    seatassignment, seatstyle = (listofseats[istudent-1], alternatingseats[istudent-1]) # DOESN'T WORK 
    
    c.setFillColor(colors.black)
# do we need a trick to get opaque bg under text?
#    t=c.beginText(-1,-1) 
#    t.setTextRenderMode(6)
#    c.drawText(t)

    c.drawString(1*inch,10.25*inch,thisname+"              "+thisemail,0)
#    c.drawString(7*inch,10.55*inch,"EXAM VERSION "+seatstyle,0)
#     c.drawString(1*inch,10.55*inch,thisname+" "+thisemail+"     SEAT "+seatassignment+"   EXAM VERSION"+seatstyle,0)
#    c.drawString(1*inch,10.35*inch,"ANSWERS MUST BE IN BLUE BOOK")
    # get list of student's wrong answers
    thisquestionlist = thisrecord.keys()
    wrongslist = []
    examset = []
# collect all the missed question in wrongslist
    for question in thisquestionlist:
        if thisrecord[question] == False:
            wrongslist.append(question)
    # different behavior needed depending on number of mistakes. 
    if len(thisquestionlist) < nneeded : # mostly-absent student
        print "student ", individual, studentids[individual], " didn't see enough Q for exam"
        continue # JUST A DEBUGGING EXPERIMENT maybe this discards the multi-clicker overwrite oddity?  If we bail out of exam generation for an absent student we won't overwrite a "good" exam with a blank one.
    elif len(wrongslist) >= nneeded  : # lots of wrong answers?  Pick N.
        examset = random.sample(wrongslist,nneeded)
    elif len(wrongslist) == nneeded : # exactly N? use all of them.
        examset = wrongslist
    else : # very few wrong answers = use all of them, plus salt in right answers too
        print "student ", individual,  studentids[individual], "only had", len(wrongslist), " wrong"
        examset = wrongslist 
        while (len(examset) < nneeded):
            howaboutthisone = random.sample(thisquestionlist,1)[0]
            if howaboutthisone not in examset:
                examset.append(howaboutthisone)
        
    print individual, studentids[individual], examset ;
            
        ########## exam sheet generation block ####################
        # At this point the array "examset" is a list of N questions
        # that this student be given.   Time to start patching together images etc.               


   # for each question we have a funny file operation
    iquadrant = 0;
    imx=0;
    imy=0;
    xwid=2.5*inch
    ywid=5*inch
    for thisquestion in examset:
        # decide where to put resulting image and how big to make it.  
        # FIXME.  This is a terrible hack and can be improved.   
        #FIXME.  Also need to implement the user-choice of grid.

        xwid = 7.5*inch/layout[0]
        ywid = 9.5*inch/layout[1]
        icol = iquadrant%layout[0]
        irow = iquadrant/layout[0]
        imx = 0.5*inch+(icol)*xwid
        imy = 0.5*inch + (layout[1]-irow-1)*ywid
        xwid = 0.95*xwid
        ywid = 0.95*ywid
        
        ## if (fullscreen and not cropleft): 
        ##     xwid=4*inch
        ##     ywid=4*inch
        ##     if (iquadrant==0):
        ##         imy = 5.25*inch; 
        ##         imx = 1*inch;
        ##     elif (iquadrant==1):
        ##         imy = 5.25*inch; 
        ##         imx = 4.5*inch;
        ## elif (fullscreen and cropleft):
        ##     xwid=2.5*inch
        ##     ywid=5*inch
        ##     if (iquadrant==0):
        ##         imy = 5.25*inch; 
        ##         imx = 1*inch;
        ##     elif (iquadrant==1):
        ##         imy = 5.25*inch; 
        ##         imx = 4.5*inch;
        ## elif (not fullscreen and not cropleft):
        ##     xwid=4*inch
        ##     ywid=4*inch
        ##     if (iquadrant==0):
        ##         imy = 5.25*inch; 
        ##         imx = 1*inch;
        ##     elif (iquadrant==1):
        ##         imy = 5.25*inch; 
        ##         imx = 4.5*inch;
        ##     elif (iquadrant==2):
        ##         imy = 0.5*inch; 
        ##         imx = 1*inch;
        ##     elif (iquadrant==3):
        ##         imy = 0.5*inch; 
        ##         imx = 4.5*inch;               
        ## elif (not fullscreen and cropleft):              
        ##     xwid=2.5*inch
        ##     ywid=5*inch
        ##     if (iquadrant==0):
        ##         imy = 5.25*inch; 
        ##         imx = 1*inch;
        ##     elif (iquadrant==1):
        ##         imy = 5.25*inch; 
        ##         imx = 4.5*inch;



        # open and place image

        screenshotfile = qfiles[thisquestion]
        print len(examset), thisquestion, screenshotfile
        im = ImageReader(screenshotfile)
        c.drawImage(im,imx,imy,width=xwid,height=ywid)
        c.setFillColorRGB(1,1,1)
        c.setStrokeColorRGB(1,1,1)
        c.rect(imx-0.05,imy+ywid-0.25*inch-0.05,0.5*inch,0.3*inch, fill=1)
        c.setStrokeColorRGB(0,0,0)
        c.drawString(imx,imy+ywid-0.25*inch,"Q1."+str(iquadrant+firstnumber),2)

        
        
        #FIXME.   need to implement the user-choice of grid.
        iquadrant+=1
        if (iquadrant > layout[0]*layout[1]-1):
            c.showPage()
            iquadrant=0
                

    if nameonbackpage:
        if (nneeded%(layout[0]*layout[1]) != 0):
            c.showPage()
        c.drawString(1*inch,10.25*inch,thisname+"              "+thisemail,0)

            
    c.save()

### Finally, use pyPDF to add the "common" pages to this file.  Need to reopen.
    individualpages = PdfFileReader(file(outputpdfname+"tmp", "rb"))
    output = PdfFileWriter()
    if prefixpages != "":
        for i in range(prefixpages.getNumPages()):
            output.addPage(prefixpages.getPage(i))
    
    for i in range(individualpages.getNumPages()):
        output.addPage(individualpages.getPage(i))

    if postfixpages != ""    :
        for i in range(postfixpages.getNumPages()):
            output.addPage(postfixpages.getPage(i))

    outputStream = file(outputpdfname,"wb") 
    output.write(outputStream)
    outputStream.close()
    remove(outputpdfname+"tmp")

### debugging log 
    print "QASSIGNED: ", thisname, thisemail, examset

#### and record this student's correct answers in a csv file for later use      

    answerkeyfile.write(thisname+ ","+ thisemail+",")
    for thisquestion in examset:
        answerkeyfile.write(correctanswersbyq[thisquestion]+",")
    for thisquestion in examset:
        answerkeyfile.write(thisquestion+",")
    answerkeyfile.write("\n")    
            
################
#  clean up and finish
################
answerkeyfile.close()
