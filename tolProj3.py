import csv
import nltk
import random
import statistics
from nltk.corpus import stopwords 
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize 

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

def isMC(questionsData, questionId): #given questions data and the question id, return if the question is a MC type; Tested
    for question in questionsData:
        if question["Question_id"] == str(questionId):
            if question["Question_type"] == "MC" or question["Question_type"] == "MC (Multiple choice)":
                return True
            else:
                return False
    print("Question ID not valid")

def isSA(questionsData, questionId): #given questions data and the question id, return if the question is a SA type; Tested
    for question in questionsData:
        if question["Question_id"] == str(questionId):
            if question["Question_type"] == "SA" or question["Question_type"] == "SA (Select all that apply)":
                return True
            else:
                return False
    print("Question ID not valid")

def individualQuestion(questionsData, questionId): # tidy up individual questions
    thisQuestion = {"Question_id":questionId}
    for question in questionsData:
        if question["Question_id"] == str(questionId):
            if isMC(questionsData, questionId): # identify question type
                thisQuestion["Question_type"] = "MC"
            if isSA(questionsData, questionId): # identify question type
                thisQuestion["Question_type"] = "SA"
            thisQuestion["Correct_answer_choice"] = dict()
            for correctChoice in list(question["Correct_answer_choice"].split(",")): # turn correct choices into a dict with corresponding texts
                thisQuestion["Correct_answer_choice"][str(correctChoice.strip())] = question["Choice_{0}_text".format(str(correctChoice).strip())]
            thisQuestion["Question_text"] = question["Question_text"]
    return thisQuestion

def addAnswerLength(questionsData, answersData): # add the answer length tag to answers data
    tokenizer = RegexpTokenizer(r'\w+')
    for answer in answersData:
        answer["Answer_length"] = len(tokenizer.tokenize(answer["Answer_text"])) # add word count to answer data
        thisQuestion = individualQuestion(questionsData, answer["Question_id"])
        correctAnswerText = ""
        if len(thisQuestion["Correct_answer_choice"]) > 1:
            for key,value in thisQuestion["Correct_answer_choice"].items(): # combine correct answer texts
                correctAnswerText += " " + value
        else:
            correctAnswerText = list(thisQuestion["Correct_answer_choice"].values())[0]
        answer["Answer_lengthRatio"] = answer["Answer_length"]/len(tokenizer.tokenize(correctAnswerText))
    return answersData

def addAnswerSimilarity(questionsData, answersData): # calculate students' answer's similarity to the correct answers' text using tokenization and cosine similarity; add this data to the student answers' entry
    for answer in answersData:
        thisQuestion = individualQuestion(questionsData, answer["Question_id"])
        correctAnswerText = ""
        if len(thisQuestion["Correct_answer_choice"]) > 1:
            for key,value in thisQuestion["Correct_answer_choice"].items(): # combine correct answer texts
                correctAnswerText += " " + value
        else:
            correctAnswerText = list(thisQuestion["Correct_answer_choice"].values())[0]
        studentAnswerText = answer["Answer_text"]
        # tokenization 
        studentAnswerText_list = word_tokenize(studentAnswerText)  
        correctAnswerText_list = word_tokenize(correctAnswerText) 
        # sw contains the list of stopwords 
        sw = stopwords.words('english')  
        l1 =[];l2 =[] 
        # remove stop words from string 
        studentAnswerText_set = {w for w in studentAnswerText_list if not w in sw}  
        correctAnswerText_set = {w for w in correctAnswerText_list if not w in sw} 
        # form a set containing keywords of both strings  
        rvector = studentAnswerText_set.union(correctAnswerText_set)  
        for w in rvector: 
            if w in studentAnswerText_set: l1.append(1) # create a vector 
            else: l1.append(0) 
            if w in correctAnswerText_set: l2.append(1) 
            else: l2.append(0) 
        c = 0
        # cosine formula  
        for i in range(len(rvector)): 
                c+= l1[i]*l2[i] 
        cosineSimilarity = c / float((sum(l1)*sum(l2))**0.5) 
        answer["Similarity"] = cosineSimilarity
    return answersData

def correctStudentText(questionsData, answersData): 
    similarities = []
    lengthRatios = []
    correctAnswers = []
    for answer in answersData:
        if answer["Student_score_on_question"] == "1": # pick the students' answer with score of 1
            thisQuestion = individualQuestion(questionsData, answer["Question_id"])
            correctAnswers.append(answer)
            similarities.append(answer["Similarity"])
            lengthRatios.append(answer["Answer_lengthRatio"])

    for answer in correctAnswers: # filter out the students' ansewrs with a similarity lower than one standard deviation of the average
        if answer["Similarity"] < (statistics.mean(similarities)-statistics.stdev(similarities)):
            correctAnswers.remove(answer)
        if ((answer["Answer_lengthRatio"] < statistics.mean(lengthRatios) - statistics.stdev(lengthRatios)) 
        or (answer["Answer_lengthRatio"] > statistics.mean(lengthRatios) + statistics.stdev(lengthRatios))): # remove answers outside of one stdev of average length
            correctAnswers.remove(answer)

    return (correctAnswers)

def incorrectStudentText(questionsData, answersData): 
    similarities = []
    incorrectAnswers = []
    for answer in answersData: # pick the students' answer with score of 0
        if (answer["Student_score_on_question"] == "0") or (answer["Student_score_on_question"] == "0.5"):
            thisQuestion = individualQuestion(questionsData, answer["Question_id"])
            similarities.append(answer["Similarity"])
            incorrectAnswers.append(answer)
    return incorrectAnswers
""" # removed because there is too few incorrect answers
    for answer in incorrectAnswers: # filter out the students' ansewrs with a similarity higher than one standard deviation of the average
        if answer["Similarity"] > (statistics.mean(similarities)-statistics.stdev(similarities)):
            incorrectAnswers.remove(answer)
"""

def generateQuestion(correctAnswers, incorrectAnswers, questionsData, questionId):
    newQuestion = {"Question_id":questionId}
    newQuestion["Question_text"] = individualQuestion(questionsData, questionId)["Question_text"]
    newQuestion["Feedback"] = " ".join(individualQuestion(questionsData, questionId)["Correct_answer_choice"].values())
    newQuestion["Correct_answer_text"] = []
    newQuestion["Incorrect_answer_text"] = []
    correctAnsPool = []
    incorrectAnsPool = []
    for ans in correctAnswers:
        if ans["Question_id"] == str(questionId):
            correctAnsPool.append(ans)
    for ans in incorrectAnswers:
        if ans["Question_id"] == str(questionId):
            incorrectAnsPool.append(ans)
    try:
        for j in random.sample(incorrectAnsPool, 3): # randomly choose three incorrect answers
            newQuestion["Incorrect_answer_text"].append(j["Answer_text"])
        for i in random.sample(correctAnsPool, 1): # randomly choose one correct answers
            newQuestion["Correct_answer_text"].append(i["Answer_text"])
        newQuestion["Question_type"] = "MC"
    except:
        for j in random.sample(incorrectAnsPool, 1): # randomly choose one incorrect answers
            newQuestion["Incorrect_answer_text"].append(j["Answer_text"])
        for i in random.sample(correctAnsPool, 3): # randomly choose three correct answers
            newQuestion["Correct_answer_text"].append(i["Answer_text"])
        newQuestion["Question_type"] = "SA"
    return newQuestion
        
questionsData = list(csv.DictReader(open("Raw Data\Questions_data_prj3_validation - Question_data.csv", encoding = "utf-8")))
answersData = list(csv.DictReader(open("Raw Data\Answers_data_prj3_validation - Answer_data.csv", encoding = "utf-8")))

# for Google colab
# questionsData = list(csv.DictReader(open("/content/Questions_data_prj3_UTF8.csv",encoding = "ISO-8859-1")))
# answersData = list(csv.DictReader(open("/content/Answers_data_prj3_update2_UTF8.csv", encoding = "ISO-8859-1")))

answersData = addAnswerLength(questionsData, answersData) # add answer length to the answers data

answersData = addAnswerSimilarity(questionsData, answersData) # add cosine similarity of students' answer to the answers data

correct = correctStudentText(questionsData, answersData)
incorrect = incorrectStudentText(questionsData, answersData)

problemSet = ""
for i in ["5","6"]:
    problemSet += ("\n--------------\n")
    for key,value in generateQuestion(correct, incorrect, questionsData, i).items():
        problemSet += str(key)+" : "+str(value) + "\n"
    problemSet += ("\n--------------\n")
writeFile("problemSet.txt",problemSet)




