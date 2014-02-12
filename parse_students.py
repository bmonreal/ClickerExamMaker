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

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

from PyPDF2 import PdfFileWriter, PdfFileReader

from PIL import Image

import Tkinter, tkFileDialog
from os import listdir, remove
from os.path import isfile, join


mypath=""
examsdir=""
prefixpdfname=""
postfixpdfname=""
rosterfilename=""
nneeded = 4
layout = [2,2] 

#########################################
##### get user input ####################
try:
    # see if there's a command-line argument
    opts, args = getopt.getopt(sys.argv,"c:o:f:l:n:",["class=","output=","prefix=","postfix="])


except getopt.GetoptError:
    print "Run parse_students with no arguments to get interactive prompts."
    print "or run (all args required)"
    print "parse_students -c <clicker class directory> -o <exam directory> -f <pdf file to prefix> -l <pdf file to postfix> -n <number of questions per student>"

for opt, arg in opts:
    # if it's a command-line invocation, parse arguments for input parameters and text-prompt for missing ones.
    if opt in ("-c","--class"):
        mypath = arg
    elif opt in ("-o,--output"):
        examsdir = arg
    elif opt in ("-f,--prefix"):
        prefixpdfname = arg
    elif opt in ("-l","--postfix"):
        postfixpdfname = arg
    elif opt in ("-n"):
        nneeded = int(arg)
       
    # if not, enter the GUI and set user input parameters there.
print 'Entering interactive mode.'
if mypath=="":
    mypath = tkFileDialog.askdirectory(title="Please select the iClicker folder for this class.")+"/"
if examsdir=="":    
    examsdir = tkFileDialog.askdirectory(title="Please select a folder in which to save the exams")+"/"
if prefixpdfname=="":
    prefixpdfname = tkFileDialog.askopenfilename(title="Please select any PDF file you want prepended to every exam.  (Cancel if none.)")
if postfixpdfname=="":    
    postfixpdfname = tkFileDialog.askopenfilename(title="Please select any PDF file you want post-pended to every exam. (Cancel if none.)")
if rosterfilename=="":
    rosterfilename = tkFileDialog.askopenfilename(title="Please find the class roster in Moodle format.")

 
# Key to grading:
# Z = Malfunctioning question, inhibit from exam generation
# AZ, BZ, CZ, DZ, EZ = inhibit from exam use BUT maybe use for gradebook

################ Input student information #################
# Step 1.   The "RemoteID.csv" file helps create a map from clickerIDs to emails
# and the "moodleroster.txt" (exported from iGrader) maps from emails to names. #  Not the best system but we can handle it.  

idfile = open(mypath+"/SessionData/RemoteID.csv");
idreader = csv.reader(idfile)
students = {}
studentids = {}
for row in idreader:
    students[row[0]] = {}
    studentids[row[0]] = row[1]  #key is clicker-ID, value is email
    print row[0], row[1]
idfile.close();

emaildb = {}
idfile = open(rosterfilename);
idreader = csv.reader(idfile,delimiter='\t')
idreader.next(); #skip first line
for row in idreader:
    print "roster = ", row;
    firstname = row[0]
    lastname = row[1]
    email = row[3]
    emaildb[email] = lastname + ", " + firstname;
emaildb['missing'] = "unregistered"
    

################ Read all clicker/class session information #############
# the goal of this read is to 
# (a) open each session file & learn the "correct" answers from the 6th row
# (b) go down the each students and add each question as a "T/F" (right wrong) to the student's answer dictionary 
# (c) accumulate a list of question-IDs to help find the question images later.

qfiles = {}

files = [ f for f in listdir(mypath+"SessionData/") if ( isfile(mypath+"SessionData/"+f) and "L" in f and "csv" in f)]
# begin loop through list of files!   
for f in files:
    print(f)
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
        if not (isfile(thisqimage)):
            print "killit"
            correctanswer[i] = "Z"

    print correctanswer    
    # OK, now I know the number of questions and the correct answers.  Time to go through the remaining rows and populate the "student answers" database.
    for row in thisfile:
        # see if this student clicker is in the dictionary already
        thisstudent = row[0]
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
    print "cropping",thisfile,thisqkey
    im = Image.open(thisfile)
    im = im.crop([45,125,290,550])
    # generate a new filename to save the crop
    newfilename = "Exams/"+thisqkey+"_crop.jpg";
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


listofstudents = students.keys();
    
istudent = 0
    

for individual in listofstudents:
    istudent += 1
    
    thisrecord = students[individual]
    thisemail = studentids[individual]
    thisname = emaildb[thisemail]
    thisnameforfile = thisname.replace(',','_').replace(' ','_').replace('__','_')
    outputpdfname = "Exams/exam"+thisnameforfile+".pdf"
    c = canvas.Canvas(outputpdfname+"tmp",pagesize=letter)
    c.drawString(1*inch,10.55*inch,thisname)
    c.drawString(1*inch,10.35*inch,thisemail)
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
    for thisquestion in examset:
        # decide where to put resulting image
        if (iquadrant==0):
            imy = 5.25*inch; 
            imx = 1*inch;
        elif (iquadrant==1):
            imy = 5.25*inch; 
            imx = 4.5*inch;


        # open and place image

        screenshotfile = qfiles[thisquestion]
        print len(examset), thisquestion, screenshotfile
        im = ImageReader(screenshotfile)
        c.drawImage(im,imx,imy,width=2.5*inch,height=5*inch)
        
        iquadrant+=1
        if (iquadrant > 1):
            c.showPage()
            iquadrant=0
                

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




################
# 
################
