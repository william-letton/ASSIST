##Program requires installatioon of SciKit from https://scikit-learn.org/stable/install.html
##Program demo can be found at https://www.datacamp.com/community/tutorials/svm-classification-scikit-learn-python

# Import necessary packages.
import time
startTime = time.time()
import math
import csv



##Define a class for articles, initialising with content(abstract),
##ID, current goldTag, and content without punctuation as a string
##and as a list of codons.
class Article:
    ##variables from LIRA
    title=""
    ID=""
    content=""
    goldTag=""
    goldAssignment=""
    ##variables calculated in classifier methods
    contentNopunctuation=""
    contentWordList=[]
    contentWordListSet=[]
    contentWord2List=[]
    codonFourList=[]
    codonThreeList=[]
    #codonFourListSet=[]
    tag_nb_codon4=""
    tag_nb_codon3=""
    #tag_nb_codon4_TFIDF=""

    tag_nb_word=""
    #tag_nb_word_TFIDF=""
    tag_nb_word2=""
    assignment_nb_codon4=""
    assignment_nb_codon3=""
    assignment_nb_word=""
    assignment_nb_word2=""
    tag_suggested=""
    assignment_suggested=""
    recommendReview=False
    prob_IN=0
    prob_IN_rank=0
    ##inital processing on initialising
    def __init__(self, content, ID, goldTag,goldAssignment):
        self.content = content
        self.ID = ID
        self.goldTag=goldTag
        self.goldAssignment=goldAssignment
        ##create no punctuation version of content
        w=""
        for character in content:
            if character not in punctuations:
                w=w+character
        w=w.lower()
        self.contentNopunctuation=w
        ##create 4-length codon from no punctuation version of content
        l=list()
        for i in range(0,len(self.contentNopunctuation)-3):
            codon=self.contentNopunctuation[i]+self.contentNopunctuation[i+1]+self.contentNopunctuation[i+2]+self.contentNopunctuation[i+3]
            #print(codon)
            l.append(codon)
        #print(l)
        self.codonFourList=l
        ##create 3-length codon from no punctuation version of content
        l2=list()
        for i in range(0,len(self.contentNopunctuation)-2):
            codon=self.contentNopunctuation[i]+self.contentNopunctuation[i+1]+self.contentNopunctuation[i+2]
            #print(codon)
            l2.append(codon)
        #print(l)
        self.codonThreeList=l2
        #print(self.codonFourList)
        ##Create a set of 4-length codons for that article.
        #self.codonFourListSet=list(set(l))
        ##create words from no punctuation version of content.
        l=list()
        split=self.contentNopunctuation.split()
        for word in split:
            l.append(word)
        self.contentWordList=l
        ##Create a set of words for that article.
        self.contentWordListSet=list(set(l))

        ##create 2-word N-grams from the words list.
        l2=list()
        for pos in range(0,len(self.contentWordList)-1):
            l2.append(self.contentWordList[pos]+" "+self.contentWordList[pos+1])
        self.contentWord2List=l2


class SVMdata:
    DESCR=""
    Data=list()
    Feature_names=list()
    Filename=""
    Target=list()
    Target_names=list()
    def __init__(self,DESCR,Data,Feature_names,Filename,Target,Target_names):
        self.DESCR=DESCR
        self.Data=Data
        self.Feature_names=Feature_names
        self.Filename=Filename
        self.Target=Target
        self.Target_names=Target_names
## Detect and flag duplicate abstracts. Ignores blank abstracts.
def flagDuplicateArticles(articles):
    print("Checking for duplicate articles...")
    dupIDList=list()
    pairList=list()
    for article1 in articles:
        if len(article1.contentNopunctuation)>10:
            if article1.ID not in dupIDList:
                for article2 in articles:
                    if article1.ID != article2.ID:
                        if article1.contentNopunctuation==article2.contentNopunctuation:
                            dupIDList.append(article1.ID)
                            dupIDList.append(article2.ID)
                            pairList.append([article1.ID,article2.ID])
    if len(dupIDList)>0:
        print("\nDuplicate articles found. ID numbers are: ",pairList)
        dupQuit=input("\nContinue analysis with duplicates? (y/n)")
        if dupQuit != "y":
            quit()
        else:
            print("Continuing analysis with duplicates...")
    else:
        print("No duplicate articles found.")
## Detact and flag duplicate abstracts with inconsitent goldTags. Ignores blank abstracts.
def compareDupArticleTags(articles):
    print("Checking for inconsistent tags within duplicated articles...")
    dupIDList=list()
    pairList=list()
    for article1 in articles:
        if len(article1.contentNopunctuation)>10:
            for article2 in articles:
                if article1.ID != article2.ID:
                    if article1.contentNopunctuation==article2.contentNopunctuation:
                        if (article1.ID not in dupIDList and article2.ID not in dupIDList):
                            pairList.append((article1.ID,article2.ID))
                            dupIDList.append(article1.ID)
                            dupIDList.append(article2.ID)
    if len(pairList)>0:
        print("Duplicate articles found. Checking human-assigned screening tag consistency...")
        noMatch=list()
        for a,b in pairList:
            for article1 in articles:
                if article1.ID == a:
                    for article2 in articles:
                        if article2.ID == b:
                            if article1.goldTag != article2.goldTag:
                                noMatch.append([a,b])
        if len(noMatch)>0:
            print("\nDuplicate articles found with non-matching human-assigned screening tags:")
            for pair in noMatch:
                pair.sort()
            for a,b in noMatch:
                for article in articles:
                    if article.ID==a:
                        print("\n")
                        print(article.ID,article.goldTag)
                for article in articles:
                    if article.ID==b:
                        print(article.ID,article.goldTag)
            getout=input("\nContinue analysis? (y/n)")
            if getout=="n":
                quit()
        else:
            print("Duplicate articles found, but assigned tags are consistent.")
    else:
        print("No duplicate articles found.")
## Create an object containing all articles + create the word codons.
def createArticles():
    ## Ask user to input the file to import and which columns within it are which.
    trainFile=input('Please enter the csv filename (including ".csv"), then press ENTER: ')
    inputColID=input('Please enter the column letter containing abstract the IDs, then press Enter: ')
    inputColAbstract=input('Please enter the column letter containing the abstracts text, then press Enter: ')
    inputColGoldTags=input('Please enter the column letter containing the gold-standard tags, then press Enter: ')
    inputColGoldAssignment=input('Please enter the column letter containing the gold-standard IN-EX assignments, then press Enter: ')
    if trainFile is "":
        trainFile = "FibratesTrainTiny.csv"
    if inputColID is "":
        inputColID = "A"
    inputColID=ord(inputColID.lower())-97
    if inputColAbstract is "":
        inputColAbstract = "B"
    inputColAbstract=ord(inputColAbstract.lower())-97
    if inputColGoldTags is "":
        inputColGoldTags = "C"
    inputColGoldTags=ord(inputColGoldTags.lower())-97
    if inputColGoldAssignment is "":
        inputColGoldAssignment = "E"
    inputColGoldAssignment=ord(inputColGoldAssignment.lower())-97
    ## Read file and create a list each for IDs, abstracts, and goldTags
    print("Now reading file...")
    try:
        with open(trainFile,encoding="ISO-8859-1") as csvfile:
            readCSV=csv.reader(csvfile,delimiter=',')
            ##create empty lists for abstracts and screening codes
            trainingIDlist=[]
            contents=[]
            goldCodes=[]
            goldAssignment=[]
            ##populate the empty lists with column data by row
            for row in readCSV:
                trainingIDlist.append(row[inputColID])
                contents.append(row[inputColAbstract])
                goldCodes.append(row[inputColGoldTags])
                goldAssignment.append(row[inputColGoldAssignment])
    except:
        print("Unable to open file. Please check filename and type.")
        input('Press ENTER to exit')
        quit()
    ##remove the first item from the list for abstracts and screening codes
    ##as this is just the column names
    contents=contents[1:]
    goldCodes=goldCodes[1:]
    trainingIDlist=trainingIDlist[1:]
    goldAssignment=goldAssignment[1:]
    ## Create an Article object for each article and store them in an object.
    allArticles=[Article(contents[i],trainingIDlist[i],goldCodes[i],goldAssignment[i]) for i in range(0,len(trainingIDlist))]
    return(allArticles)
##Using the data in the articles object, create an object for SVM data.
def createSVMdata(articles):
    ##Create the variable names.
    DESCR=""
    Data=list()
    Feature_names=list()
    Filename=""
    Target=list()
    Target_names=list()
    ##Process the articles to produce the variables for creating the SVMdata object.
    ##Feature_names is the vocabulary list.
    for article in articles:
        for word in article.contentWordListSet:
            Feature_names.append(word)
    Feature_names=list(set(Feature_names))
    Feature_names.sort()

    ##Data is a list of lists. for each article it contains a 1 or 0 for presence
    ##of each word in the article.
    for article in articles:
        ## Create a list equal in length to the Feature_names, with a value of 0
        ## in each position
        wordVector=[0]*len(Feature_names)
        ## For each word in the article word list set, change the value of the index
        ## equivalent to the Feature_names to 1.
        for word in article.contentWordListSet:
            pos=Feature_names.index(word)
            wordVector[pos]=1
        Data.append(wordVector)

    ##Target is the list of assignments, 1 for IN, 0 for EX.
    for article in articles:
        if article.goldAssignment=="IN":
            Target.append(1)
        elif article.goldAssignment=="EX":
            Target.append(0)
        else:
            print("ERROR, assignment other than IN or EX detected.")
            input("Press ENTER to quit")
            quit()

    ##Target_names is a list of the assignments, where the index matches the integer
    ##values in the Target list (e.g. if IN is 1 and EX is 0 in Target, then indexes
    ##0 and 1 in Target_names are "EX" and "IN")
    Target_names.append("EX")
    Target_names.append("IN")

    ##Finally, create the data object and return it.
    obOut=SVMdata(DESCR,Data,Feature_names,Filename,Target,Target_names)
    return(obOut)
##Perform the SVM classification on the data
def SVMclassification(dataset):
    # Import train_test_split function.
    from sklearn.model_selection import train_test_split

    # Split dataset into training set and test set. 70% training and 30% test.
    x_train, x_test,y_train,y_test=train_test_split(dataset.Data,dataset.Target,test_size=0.3,random_state=109)
    print("len(x_train)")
    print(len(x_train))
    print("len(x_test)")
    print(len(x_test))
    print("len(y_train)")
    print(len(y_train))
    print("len(y_test)")
    print(len(y_test))

    # Import svm model
    from sklearn import svm

    # Create a svm Classifier. Linear Kernel
    clf = svm.SVC(kernel='linear')

    #Train the model using the training sets
    clf.fit(x_train,y_train)

    #Predict the response for test dataset
    y_pred = clf.predict(x_test)

    # Import scikit-learn metrics module for accuracy calculation
    from sklearn import metrics

    # Model Accuracy: how often is the classifier correct?
    print("Accuracy: ",metrics.accuracy_score(y_test,y_pred))

    # Model Precision: what percentage of positively labelled tuples are actually positive?
    print("Precision: ",metrics.precision_score(y_test,y_pred))

    #Model Recall: What percentage of positive tuples are labelled as positive?
    print("Recall: ",metrics.recall_score(y_test,y_pred))




### Run the program

## Define punctuations to be removed from analysis.
punctuations = "_çìëá•™©!£$€/%^&*+±=()â‰¥[]|0123456789'=.,:;?%<>ÿòñ~#@-—–{}úøîæ÷ó¬åà®¯§"+'"“”'

##Import articles and create an object containing them all.
trainingArticles=createArticles()

##Handle duplicates and non-consistent tagging.
flagDuplicateArticles(trainingArticles)
compareDupArticleTags(trainingArticles)

##Create the SVMdata object from the articles list.
FibratesData=createSVMdata(trainingArticles)

##Print the contents of FibratesData.
#print("FibratesData.DESCR")
#print(FibratesData.DESCR)
#print("FibratesData.Data")
#print(FibratesData.Data)
#print("FibratesData.Feature_names")
#print(FibratesData.Feature_names)
#print("FibratesData.Filename")
#print(FibratesData.Filename)
#print("FibratesData.Target")
#print(FibratesData.Target)
#print("FibratesData.Target_names")
#print(FibratesData.Target_names)

##Run the SVM classifier.
SVMclassification(FibratesData)

##Report on program runtime.
print("Program took",int(time.time()-startTime),"seconds to run.")

##Prompt to exit program.
input('Press ENTER to exit')
