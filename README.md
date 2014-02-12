ClickerExamMaker

This is a Python script that can parse a set of i>Clicker sessions, find questions that each student has gotten wrong, and (by cropping regions from the i>Clicker screenshots) generate a custom midterm exam for that student.

################# The basic idea ###############
Here is how the code works:

Tell the program where to find your i>Clicker class folder.  (It will prompt you.)

The program will read all of the "SessionData" csv files and build a list of students and the questions they got wrong.  Each question is associated with a *screenshot* of what your computer was displaying when the question was asked.  The program will grab several of these screenshots (the whole screen, or a specific part of the screen that you specify) and paste them together into a PDF file.   

The code then tries to find the students' names (currently by parsing the file SessionData/RemoteID.csv and the file moodleroster.txt) and will print the name and email address at the top of each page.  

That PDF file is now a custom exam for that student, forcing them to re-answer clicker questions that had previously given them trouble!

The code automatically repeats this for every student (specifically, for every clicker-ID) and leaves you with a folder full of PDFs.

The code will also append (both prepend and postpend) any additional PDF files you specify.   For example, the first midterm I used this for began with of 2 "customized" pages (four questions, chosen student-by-student) and 3 additional "common" pages (three questions answered by all the students).   


############# Important details for use ################
############# PLEASE READ COMPLETELY    ################

1) The software needs to know the correct answers.  

In order to select "questions the student got wrong", rather than "random questions", the program needs to know the right and wrong answers to all the questions.  If you have not done so already YOU NEED TO ENTER THE RIGHT ANSWERS.   Where do you enter them?  The easiest place to do this is by editing the CSV files beginning with "L" found in the SessionData folder.  Open each of these files in Excel or another spreadsheet program.   Add the correct answer letters to the appropriate cells in the 5th row---cell D5 for the first question, J5, P5, V5, etc..   
2) You can flag questions for inclusion or exclusion from the exams. 

 To exclude a question, add the letter "Z" to the answer field.  "CZ" is a question whose correct answer is C but which will not be used on exams.  (I did this to abnormally-easy or abnormally-hard questions that had specific pedagogical roles in class, but aren't appropriate for exams.)   

3) Your class roster needs to be in EXACTLY the format that I used.  The SessionData/RemoteID.csv file should be fine (it's autogenerated by iClicker) and the "roster" file should be fine if you export it directly from Moodle and don't mess with it.   But please double-check!

The "SessionData/RemoteID.csv" file has to have two columns:
Column 1 = clicker ID number
Column 2 = student email address or other unique identifier

#06DE60B8,"davidortiz@umail.ucsb.edu"
#378E2B92,"pedromartinez@umail.ucsb.edu"
#843767D4,"dustinpedroia@umail.ucsb.edu"
#84866664,"billmueller@umail.ucsb.edu"
etc.

The "moodleroster.txt" file must be a TAB-SEPARATED file with the following format exactly:

"First name"	"Last name"	"ID number"	"Email address"
David	"Ortiz Arias"	1234244	davidortiz@umail.ucsb.edu
Pedro	Martinez	3030222	pedromartinez@umail.ucsb.edu
William	Mueller	2342323	billmueller@umail.ucsb.edu
Dustin Pedroia	2322777	dustinpedroia@umail.ucsb.edu

The first ROW is discarded.  Make sure there isn't a student name in the first row!   
The first column is firstnames, including quotes around anything complicated 
The second column is surnames, including quotes around anything complicated
The third column is discarded.
The fourth column must be the SAME EMAIL ADDRESSES OR WHATEVER as in the clicker registrations file!   This is the key we use for matching things up.   

4) You must have consistent 1024x768-pixel screenshots of the questions as they were shown to the students.   These screenshots are found in the "Images" folder in your class folder, and they end in "Q#.jpg".  (Check the size!)   There are two ways the code can handle these screenshots: 

Fullscreen or not?  
a) If these screenshots show the same thing that the class sees, you want the variable fullscreen = True.
b) If these screenshots show a "presenter display", you want the variable fullscreen = False.  This is currently set up for Keynote '09 presenter displays and YOU WILL HAVE TO MODIFY THE CODE to do anything else.   Contact the author (bmonreal@physics.ucsb.edu) if you need help.  

Cropleft or not?   Does the exam need the exact thing the class saw before, or part of it?  
a) If the exam is meant to exactly reuse the clicker question, leave this cropleft = False
b) A fun special case: I always construct clicker slides with the question on the left half of the screen and the multiple-choice answers on the right.   By setting "cropleft=True", I show only the *question* on the printed exams---it turns things from multiple-choice into long-answer.



