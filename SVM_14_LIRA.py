##Program requires installatioon of SciKit from https://scikit-learn.org/stable/install.html
##Program demo can be found at https://www.datacamp.com/community/tutorials/svm-classification-scikit-learn-python

##Input the starting parameters for runnign the classifier.
##Define the number of classifiers to be trained for the commitee. Published
##research suggests that 2 is usually optimal.
numClassifiers=2

##Define the proportion of eligiable abstracts to use for classifier training,
##(after correcting for class imbalance). This can be reduced from 1 if there
##is a particularly large dataset, and will train the classifier with a subset of
##the data.
trainProp=1

##Define the threshold of mean classifier vote required for inclusion (as a proportion of 1).
##Increasing this value will increase the recall, but may decrease the Cohen's Kappa. This
##value is used as a starting point for the paramter optimisation.
startingThreshold=0.99

##Define the minimum acceptible recall (sensitivity) for the overall classifier.
##The higher this value the greater the sensitivity the final classifier will have,
##at the expense of accuracy and Kappa. Setting the minRecall to 0 will result in
##parameters that are optimised just based on Kappa scores.
minRecall=0.8

##define initial log parameter range. This will define the search grid area for the
##iniital C and gamma parameter search, as well as the scaling of refining searches.
initialParamRange=4

##Define how many iterations of the C and gamma parameter optimiser we want.
nestedIterations=2

## Define punctuations to be removed from abstract text before analysis.
punctuations = "_çìëá•™©!£$€/%^&*+±=()â‰¥[]|0123456789'=.,:;?%<>ÿòñ~#@-—–{}úøîæ÷ó¬åà®¯§"+'"“”'


##############################################################

# Import necessary packages.
import time
import math
import csv
import random
from random import seed
seed(1)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
# Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics

##Record the time that the program started.
startTime = time.time()

##############################################################


##Prepare the class structure for the abstracts, and for the data object to be
##used by the SVM classifier.

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
    contentWord2ListSet=[]
    codonFourList=[]
    codonThreeList=[]
    codonFourListSet=[]
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
    ##SVM attributes
    SVMtrainIN=False
    SVMtrainEX=False
    SVMvote_sum=0
    SVMvote_count=0
    SVMvote_mean=0
    SVMvote_decision=0
    SVM_recommendReview=False
    SVM_recommendReview_random=False
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
        self.codonFourListSet=list(set(l))
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
        self.contentWord2ListSet=list(set(l2))
##Define a class for the article data, in the form that the sklearn SVM functions
##requires their input. In general this is in the form of lists where each index
##corresponds to each article.
class SVMdata:
    DESCR=""
    IDs=list()
    Data=list()
    Feature_names=list()
    Filename=""
    Target=list()
    Target_names=list()
    #Votes=list()
    def __init__(self,DESCR,IDs,Data,Feature_names,Filename,Target,Target_names):
        self.DESCR=DESCR
        self.IDs=IDs
        self.Data=Data
        self.Feature_names=Feature_names
        self.Filename=Filename
        self.Target=Target
        self.Target_names=Target_names
        #self.Votes=[[0]]*len(IDs)

###############################################################

##Define functions.

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

## In the Article object, mark the article that will be used as the training set
## for both SVM paramter optimisation and actual classification.
##There must be an equal number of INs and EXs to avoid class imbalance.
##There must be a number equal to the training proportion specified.
##There must be a number that can be divided equally into the number of classifiers
##specified.
def PickTrainingArticles(articles,numClassifiers=2,trainProp=1):
    seed(1)
    ##define lists contain the IDs of the articles of each class
    INlist=list()
    EXlist=list()
    ##count up the articles for each class.
    for article in articles:
        if article.goldAssignment=="IN":
            INlist.append(article.ID)
        elif article.goldAssignment=="EX":
            EXlist.append(article.ID)
    ##randomise both lists.
    random.shuffle(INlist)
    random.shuffle(EXlist)
    print("number of IN articles in dataset: ",len(INlist))
    print("number of EX articles in dataset: ",len(EXlist))
    ##calculate the length of the smaller class and truncate the larger to be the same.
    print("Correcting class imblance...")
    if len(INlist)<len(EXlist):
        del EXlist[len(INlist):]
    else:
        del INlist[len(EXlist):]
    print("number of IN articles in dataset: ",len(INlist))
    print("number of EX articles in dataset: ",len(EXlist))
    ##Reduce the size of the training lists based on the trainProp argument.
    print("Reducing the size of training sets according to defined proportion...")
    print("Defined proportion is: ",trainProp)
    reduceByTrainPop=int(len(INlist)//(1/trainProp))
    del EXlist[reduceByTrainPop:]
    del INlist[reduceByTrainPop:]
    print("number of IN articles in dataset: ",len(INlist))
    print("number of EX articles in dataset: ",len(EXlist))
    ##Reduce the size of the training lists so that they can be evenly split by
    ##the number of classifiers.
    print("Reducig the size of training sets to match classifier training set size.")
    print("Defined number of classifiers is: ", numClassifiers)
    reduceByClassifierNum=int(len(INlist)%(numClassifiers))
    del EXlist[len(EXlist)-reduceByClassifierNum:]
    del INlist[len(INlist)-reduceByClassifierNum:]
    print("number of IN articles in dataset: ",len(INlist))
    print("number of EX articles in dataset: ",len(EXlist))
    ##Flag each of the training articles that are left as for training.
    for id in EXlist:
        for article in articles:
            if article.ID==id:
                article.SVMtrainEX=True
    for id in INlist:
        for article in articles:
            if article.ID==id:
                article.SVMtrainIN=True

##Using the data in the articles object, create an object for SVM data.
def createSVMdata(articles,dataUnits):
    print("Creating SVM data from articles object...")
    ##Create the variable names.
    DESCR=""
    Data=list()
    IDs=list()
    Feature_names=list()
    Filename=""
    Target=list()
    Target_names=list()
    Training_articles=list()

    ##Process the articles to produce a list of which are training articles.
    for article in articles:
        if article.SVMtrainEX==True or article.SVMtrainIN==True:
            Training_articles.append(1)
        else:
            Training_articles.append(0)

    ##Process the articles to produce a list of IDs.
    for article in articles:
        IDs.append(article.ID)

    ##Process the articles to produce the variables for creating the SVMdata object.
    ##Feature_names is the vocabulary list. Input parameter chooses which data is used.
    for article in articles:
        if article.SVMtrainEX==True or article.SVMtrainIN==True:

            if dataUnits=="word":
                for word in article.contentWordListSet:
                    Feature_names.append(word)
            elif dataUnits=="word2":
                for word in article.contentWord2ListSet:
                    Feature_names.append(word)
            elif dataUnits=="codon4":
                for word in article.codonFourListSet:
                    Feature_names.append(word)
    Feature_names=list(set(Feature_names))
    Feature_names.sort()
    #print("vocabulary: ",Feature_names)
    print("Length of vocabulary: ",len(Feature_names))
    ##Data is a list of lists. for each article it contains a 1 or 0 for presence
    ##of each word in the article.
    for article in articles:
        ## Create a list equal in length to the Feature_names, with a value of 0
        ## in each position
        #wordVector=np.bool_([False]*len(Feature_names))
        wordVector=[False for i in range(0,len(Feature_names))]
        #print("wordVector :",wordVector)
        #print("wordVector type is: ",type(wordVector))
        #print("wordVector length is: ",len(wordVector))
        #print(type(wordVector[0]))
        #quit()
        ## For each word in the article word list set, change the value of the index
        ## equivalent to the Feature_names to 1. Ignore words that are not in Feature_names.
        ##The try/except blocks are to handle ignoring words that are not in the Feature_names,
        ##(i.e. not found in the articles selected to be the training set.)
        if dataUnits=="word":
            for word in article.contentWordListSet:
                try:
                    pos=Feature_names.index(word)
                    wordVector[pos]=True
                except:
                    continue
        elif dataUnits=="word2":
            for word in article.contentWord2ListSet:
                try:
                    pos=Feature_names.index(word)
                    wordVector[pos]=1
                except:
                    continue
        elif dataUnits=="codon4":
            for word in article.codonFourListSet:
                try:
                    pos=Feature_names.index(word)
                    wordVector[pos]=1
                except:
                    continue
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
    obOut=SVMdata(DESCR,IDs,Data,Feature_names,Filename,Target,Target_names)
    return(obOut)

## The function uses the SVM data that only contains the training data to create
## a list of lists of IDs, where each list contains equal numbers of IN and EX training
## example IDs and each list is the same length.
def CreateTrainingData(dataset,numClassifiers=2):
    seed(2)
    ##Create a list for all IN IDs and one for all EX IDs
    AllIDs_IN=list()
    AllIDs_EX=list()
    ##ADD the IDs for all  input articles to their respectie list.
    for pos in range(0,len(dataset.Target)):
        if dataset.Target[pos]==1:
            AllIDs_IN.append(dataset.IDs[pos])
        else:
            AllIDs_EX.append(dataset.IDs[pos])

    ##Randomise the include and exclude ID lists.
    random.shuffle(AllIDs_IN)
    random.shuffle(AllIDs_EX)

    ##Print the lists to check them.
    #for pos in range(0,len(FibratesData.Target)):
    #    print(FibratesData.Target[pos])
    #    print(FibratesData.IDs[pos])
    #print(AllIDs_IN)
    #print(AllIDs_EX)

    ##Truncate both lists to be half the length of the specified training set size.
    #totalAbstracts=len(dataset.Target)
    #print("Total abstracts to classify: ",totalAbstracts)
    #print("Proportion to use to train: ",trainProp)

    ##divide the trainProp by 2 to calculate the max number of each class (IN and EX).
    #maxAbstracts=int(totalAbstracts*trainProp/2)
    ##Truncate both lists if they are above that length
    #if len(AllIDs_IN)>maxAbstracts:
    #    del AllIDs_IN[maxAbstracts:]
    #if len(AllIDs_EX)>maxAbstracts:
    #    del AllIDs_EX[maxAbstracts:]

    ##Define the number of abstracts in the smaller class.
    #numInSmallerClass=0
    #INexcess=len(AllIDs_IN)-len(AllIDs_EX)
    #if INexcess >=0:
    #    numInSmallerClass=len(AllIDs_EX)
    #if INexcess <0:
    #    numInSmallerClass=len(AllIDs_IN)

    ##Check there are enough abstracts in the smaller class for at least one
    ## Per classifier.
    #if numInSmallerClass<numClassifiers:
    #    print("\nNot enough abstracts in minority class to train",numClassifiers,"classifiers.")
    #    print("Reducing the number of classifiers to" ,numInSmallerClass,".\n")
    #    numClassifiers=numInSmallerClass



    ##Truncated the longer list so that it is the same length as the IN list.
    #if len(AllIDs_EX)>len(AllIDs_IN):
    #    AllIDs_EX=AllIDs_EX[:len(AllIDs_IN)]
    #if len(AllIDs_IN)>len(AllIDs_EX):
    #    AllIDs_IN=AllIDs_IN[:len(AllIDs_EX)]

    ##Define how many pairs of INEX abstract pairs will be fed for training into each
    ## classifier.
    print("numClassifiers: ",numClassifiers)
    absPerClassifier=len(AllIDs_IN)//numClassifiers
    print("absPerClassifier: ",absPerClassifier)
    print("Total abstracts used for training: ",(numClassifiers*absPerClassifier*2))

    ##create include ID list sublists of the correct length to yield the same number
    ##of sublists are there are desired classifiers.
    INIDs_rand=list()
    EXIDs_rand=list()
    for i in range(0,len(AllIDs_IN), absPerClassifier):
        INIDs_rand.append(AllIDs_IN[i:i+absPerClassifier])
        EXIDs_rand.append(AllIDs_EX[i:i+absPerClassifier])

    #print("shuffled, paired INEX training lists")
    #print(INIDs_rand)
    #print(EXIDs_rand)


    ## Remove the last sublist if it is not full.
    #if len(INIDs_rand)>numClassifiers:
    #    del INIDs_rand[-1]
    #    del EXIDs_rand[-1]

    #print("shuffled, paired INEX training lists")
    #print(INIDs_rand)
    #print(EXIDs_rand)

    ## Merge IN and EX ID lists (the assignment will be looked up from the ID later).
    IDgroups=list()
    for pos in range(0,len(INIDs_rand)):
        IDgroups.append(INIDs_rand[pos]+EXIDs_rand[pos])

    ## Check the number of training groups and reduce down the the requested number
    ## of classifiers. This is because each group will have an even number of IDs
    ## (to match IN and EX numbers), and all groups have to have the same number.
    ## Therefore at this point there might be a higher number of groups than requested.
    ## e.g. If there are 50 abstracts, 25 IN and 25 EX, and 10 classifiers are requested,
    ## This will mean that training abstracts will be in groups of 4, which will give 12
    ## groups in total. The next hightest group number would be 6, but that would only give
    ## 8 groups, which is fewer than requested.
    ##return ID lists.
    while len(IDgroups)>numClassifiers:
        del IDgroups[-1]

    ## Return the list of ID number groups.
    return(IDgroups)

## using the SVM dataset, the defined training ID groups, and input parameters for
## C and gamma, run the pre-determined number of classifiers and place the probability
## Results back into the articles object.
def RunClassifiers(SVMdata,trainingIDgroups,params,articles):
    ##First remove any previous classifier probabilities.
    for article in inputArticles:
        article.SVMvote_sum=0
        article.SVMvote_count=0
        article.SVMvote_mean=0
        article.SVMvote_decision=0

    ##Train and test a classifier with a single training group, Adding class probabilities
    ##to the articles class data.
    def RunClassifier (SVMdata,trainingIDgroup,params,articles):
        print("\nTraining classifier...")

        ##Create a list each for the Data (words vector) and Target (assingment vector)
        ## for the test and train IDs.
        Xtrain=list()
        Ytrain=list()
        Xtest=list()
        Ytest=list()
        YID=list()
        ##Add the data from the dataset to either the training or testing XY sets
        ##based on whether they appear in the trainingIDgroup that has been passed
        ##to the function.
        ##For each position in the IDs list.
        for pos in range(0,len(SVMdata.IDs)):
            ##If the ID at that position is in the training group list.
            if SVMdata.IDs[pos] in trainingIDgroup:
                ##Add the data vector to the training list.
                Xtrain.append(SVMdata.Data[pos])
                ##Add the assignment value to the training list.
                Ytrain.append(SVMdata.Target[pos])
            else:
                ##OTherwise add them to the testing lists.
                Xtest.append(SVMdata.Data[pos])
                Ytest.append(SVMdata.Target[pos])
                ##Make a list of the testing set IDs too, so that the votes can be
                ## assigned after predictions have been made
                YID.append(SVMdata.IDs[pos])
        #print("YID: ",YID)
        #print("trainingIDgroup: ",trainingIDgroup)
        #print("Ytrain: ",Ytrain)
        #print("Ytest: ",Ytest)
        # Import svm model
        from sklearn import svm

        # Create a svm Classifier. Linear Kernel
        clf = svm.SVC(kernel='rbf',C=params['C'],gamma=params['gamma'],probability=True,random_state=7)

        #Train the model using the training sets
        clf.fit(Xtrain,Ytrain)

        #Predict the response for test dataset. This returns the probability of the
        ##sample for each class in the model. The columns correspond to the classes
        ##in sorted order, as they appear in the attribute classes_
        print("Making predictions...")
        Yout = clf.predict_proba(Xtest)
        #print("Yout: ",Yout)
        Ypred = list()
        for pos in Yout:
            Ypred.append(pos[1])
        #print("Ypred: ",Ypred)


        #print("Mean number of IN assignments made by classifier: ",sum(Ypred))
        #print("Total number of assignments made by classifier: ",len(Ypred))
        #print("Propotion of IN assignments made by classifier: ",(sum(Ypred)/len(Ypred)))



        ##For each of the testing abstracts, place the vote back into the original
        ## articles object.
        for article in inputArticles:
            for pos in range(0,len(Ypred)):
                #print("Current article ID: ",article.ID)
                if article.ID == YID[pos]:
                    #print("Article ID matches the Ytest list at this position")
                    #print("Vote added for article ID",YID[pos],":",Ypred[pos])
                    article.SVMvote_sum=article.SVMvote_sum+Ypred[pos]
                    article.SVMvote_count=article.SVMvote_count+1
    for group in trainingIDgroups:
        RunClassifier(SVMdata,group,params,articles)
    ##Finally, calculate the mean votes currently present for each article.
    for article in articles:
        article.SVMvote_mean=article.SVMvote_sum/article.SVMvote_count

##USe the mean probabiltiy values already calculated and stored inside the articles
##object to calculate the recall and then adjust the threshold until the recall is
##above the specified minimum.
def AdjustThresholdForRecall(articles,startingThreshold,minRecall):
    print("adjusting for recall...")
    from sklearn import metrics
    ##Apply the intial threshold in order to produce SVM decisions.
    currentThreshold=startingThreshold
    recallMet=False
    ##Define a loop that will measure the recall, and incrementally decrease the
    ##threshold until the minimum recall is reached. It then continues searching,
    ##updating teh values if it finds a better threshold.
    ##First define three variables to store the current best threshold,
    ## the best Kappa value from it, and the best Recall value from it.
    bestKappa=0
    bestRecall=0
    bestThreshold=0
    currentRecall=0
    while currentRecall<1:
        ##First use the mean vote and the current threshold to make an IN-EX
        ## assignemnt for each article.
        for article in articles:
            if article.SVMvote_mean>=currentThreshold:
                article.SVMvote_decision=1
            else:
                article.SVMvote_decision=0
        ##Calculate the Recall and kappa
        inputGoldAssListBool=list()
        SVMassListBool=list()
        for article in inputArticles:
            if article.goldAssignment=="IN":
                inputGoldAssListBool.append(1)
            else:
                inputGoldAssListBool.append(0)
            SVMassListBool.append(article.SVMvote_decision)
        currentRecall=metrics.recall_score(inputGoldAssListBool,SVMassListBool)
        currentKappa=metrics.cohen_kappa_score(inputGoldAssListBool,SVMassListBool)
        #print("Current threshold: ",currentThreshold)
        #print("Current recall: ",currentRecall)
        #print("Current Kappa: ", currentKappa)
        if currentRecall>=minRecall:
            #print("Acceptible recall.")
            ##Update the output threshold, recall, and kappa if the scores are better
            ##than those already scored.
            if currentKappa>=bestKappa:
                #print("Current kappa better than stored best. Updating...")
                bestKappa=currentKappa
                bestRecall=currentRecall
                bestThreshold=currentThreshold
        #else:
            #print("Recall not acceptible")
        ##Lower the threshold for the next loop.
        currentThreshold=currentThreshold*0.95

    ##Now apply the optimsised threshold value. This is only necessary for the
    ## final classifier, but shouldn't add much to runtime to do each time.
    for article in articles:
        if article.SVMvote_mean>=bestThreshold:
            article.SVMvote_decision=1
        else:
            article.SVMvote_decision=0

    ##Now print the best kappa and recall combination and the threshold that gave it.
    print("Final recall: ",bestRecall)
    print("Final Kappa: ", bestKappa)
    print("Final Threshold: ",bestThreshold)
    return({"Recall":bestRecall,"Kappa":bestKappa,"Threshold":bestThreshold})

##USe the mean probabiltiy values already calculated and stored inside the articles
##object to calculate the kappa for a range of threshold values.
def AdjustThresholdForKappa(articles,startingThreshold):
    print("adjusting for kappa...")
    from sklearn import metrics
    ##Apply the intial threshold in order to produce SVM decisions.
    currentThreshold=startingThreshold
    ##Define a loop that will measure the kappa, and then incrementally decrease
    ##the threshold until all articles get through.
    ##First define three variables to store the current best threshold,
    ## the best Kappa value from it, and the best Recall value from it.
    bestKappa=0
    bestRecall=0
    bestThreshold=0
    currentINprop=0
    while currentINprop<1:
        #print("Searching...")
        ##First use the mean vote and the current threshold to make an IN-EX
        ## assignemnt for each article.
        currentIN=0
        currentEX=0
        for article in articles:
            if article.SVMvote_mean>=currentThreshold:
                article.SVMvote_decision=1
                currentIN+=1
            else:
                article.SVMvote_decision=0
                currentEX+=1
        ##Calculate the current proprotion included.
        currentINprop=currentIN/(currentIN+currentEX)
        ##Calculate the Recall and kappa
        inputGoldAssListBool=list()
        SVMassListBool=list()
        for article in inputArticles:
            if article.goldAssignment=="IN":
                inputGoldAssListBool.append(1)
            else:
                inputGoldAssListBool.append(0)
            SVMassListBool.append(article.SVMvote_decision)
        currentRecall=metrics.recall_score(inputGoldAssListBool,SVMassListBool)
        currentKappa=metrics.cohen_kappa_score(inputGoldAssListBool,SVMassListBool)
        #print("Current threshold: ",currentThreshold)
        #print("Current recall: ",currentRecall)
        #print("Current Kappa: ", currentKappa)
        ##Update the output threshold, recall, and kappa if the kappa are better
        ##than those already scored.
        if currentKappa>=bestKappa:
            #print("Current kappa better than stored best. Updating...")
            bestKappa=currentKappa
            bestRecall=currentRecall
            bestThreshold=currentThreshold
        #else:
            #print("Recall not acceptible")
        ##Lower the threshold for the next loop.
        currentThreshold=currentThreshold*0.95

    ##Now apply the optimsised threshold value. This is only necessary for the
    ## final classifier, but shouldn't add much to runtime to do each time.
    for article in articles:
        if article.SVMvote_mean>=bestThreshold:
            article.SVMvote_decision=1
        else:
            article.SVMvote_decision=0

    ##Now print the best kappa and recall combination and the threshold that gave it.
    print("Final recall: ",bestRecall)
    print("Final Kappa: ", bestKappa)
    print("Final Threshold: ",bestThreshold)
    return({"Recall":bestRecall,"Kappa":bestKappa,"Threshold":bestThreshold})

## Run optimiser. This takes a list of 3 parameter combinations (C and gamma), along
## with the SVM data object and a list of training group IDs, and returns the
## C and gamma combination that gave the highest kappa once the results were thresholded
## for minimum recall.
def TripleParamsOptimiser(params,SVMdata_full,trainingIDgroups):
    ##run each set of parameters through the classifier and adjust for recall.
    for param in params:
        RunClassifiers(SVMdata_full,trainingIDgroups,param,inputArticles)
        SVMmetrics=AdjustThresholdForKappa(inputArticles,startingThreshold)
        param.update(SVMmetrics)
        print(params)
    ##pull out the C and gamma values from the dictionary with the highest kappa.
    kappaList=list()
    for paramcomb in params:
        kappaList.append(paramcomb["Kappa"])
    print("kappaList: ",kappaList)
    indexMaxKappa=kappaList.index(max(kappaList))
    print(indexMaxKappa)
    bestParams={"C":params[indexMaxKappa]["C"],"gamma":params[indexMaxKappa]["gamma"]}
    print("bestParams: ",bestParams)
    return(bestParams)

##Create inital C and gamma parameters for optimisation. This will output a list
##of dictionaries, each with a pairwise combination of 3 C and gamma parameter values.
## the range argument will give the number of orders of magnitude the values will span.
def CreateInitialParams(range=10):
    ##Define a list of real numbers to use as exponents
    expValues=[0-(range/2),0,(range/2)]
    ##Use these as exponents for a log scale.
    paramValues=list()
    for val in expValues:
        paramValues.append(10**val)
    print("paramValues :",paramValues)
    ##create a dictionary holding all combinations of C and gamma values based on
    ##the three values.
    paramsGrid=list()
    for val1 in paramValues:
        for val2 in paramValues:
            print({"C":val1,"gamma":val2})
            paramsGrid.append({"C":val1,"gamma":val2})
    return(paramsGrid)

##Input is a dictionary of a C and gamma parameter values. The funtion takes these
##values, along with a range argument to output a new 3x3 grid of parameters for
##optimisation.
def UpdateParamsGrid(optParams,range=5):
    ##pull out the parameter values.
    Copt=optParams["C"]
    gammaOpt=optParams["gamma"]
    print("Copt: ",Copt)
    print("gammaOpt: ",gammaOpt)
    ## take the log of these values
    Copt=math.log(Copt,10)
    gammaOpt=math.log(gammaOpt,10)
    print("Copt: ",Copt)
    print("gammaOpt: ",gammaOpt)
    ##define a range of expValues for each parameter.
    CexpValues=[Copt-(range/2),Copt,Copt+(range/2)]
    gammaExpValues=[gammaOpt-(range/2),gammaOpt,gammaOpt+(range/2)]
    ##Use these as exponents for a log scale.
    CNewParamValues=list()
    for val in CexpValues:
        CNewParamValues.append(10**val)
    gammaNewParamValues=list()
    for val in gammaExpValues:
        gammaNewParamValues.append(10**val)
    #print("paramValues :",paramValues)
    ##create a dictionary holding all combinations of C and gamma values based on
    ##the three values.
    paramsGrid=list()
    for val1 in CNewParamValues:
        for val2 in gammaNewParamValues:
            print({"C":val1,"gamma":val2})
            paramsGrid.append({"C":val1,"gamma":val2})
    return(paramsGrid)

##takes grid of C and gamma parameters, runs the optimiser, then takes the optimal pair
##of parameters, generates a new smaller grid around them and runs the optimiser again.
##This repeats the specified number of times given as nestedIterations, refinine the
##log range by the factor given by refineRangeFactor each time.
def NestedParamsOptimisation(paramsGrid,SVMdata_full,trainingIDgroups,initialParamRange,nestedIterations=3,refineRangeFactor=2):
    count = 0
    while count<nestedIterations:
        count=count+1
        print("Round ",count," of ",nestedIterations," in nested parameter optimisation...")
        optParams=TripleParamsOptimiser(paramsGrid,SVMdata_full,trainingIDgroups)
        print("OptParams",optParams)

        paramsGrid=UpdateParamsGrid(optParams,range=(initialParamRange/(refineRangeFactor**count)))
        print("UpdatedParams: ",paramsGrid)
    return(optParams)

##Based on the current SVMvote_decision and the goldAssignment of each article in
##inputArticles, recommend those that are gold EX and voted as IN for further human
##review.
def SVM_recommendReview(articles):
    k=0
    for article in articles:
        if article.goldAssignment=="EX" and article.SVMvote_decision==1:
            article.SVM_recommendReview=True
            k+=1
    print("Number of articles recommended for review: ",k)
    return(k)

##Makes review recommendations at random (of gold-standard Excludes), given a desired number.
def SVM_recommendReview_random(articles,numReturn):
    random.seed(7)
    ##First set all random recommended reviews to False.
    for article in articles:
        article.SVM_recommendReview_random=False
    ##Now assign True values to the appropriate number of articles.
    countArticle=len(articles)
    posList=list()
    while len(posList)<numReturn:
        value=random.randint(0,countArticle-1)
        #print(value)
        if articles[value].SVM_recommendReview_random==False and articles[value].goldAssignment=="EX":
            articles[value].SVM_recommendReview_random=True
            posList.append(value)
    print("Number of random review recommendations made: ",len(posList))

##Export t the results of the classifier into two files. The first contains just
##which articles have been recommended for review. The other contains the key as
##to which of those recommendations are based on the analysis or made at random.
def exportRecommendations(articles):
    print("Exporting suggested tag results...")
    ids=["ID"]
    abs=["AbstractText"]
    gtags=["GoldTag"]
    gAssignment=["GoldAssignment"]
    #stags_codon4=["suggestedTag_codon4"]
    #stags_codon3=["suggestedTag_codon3"]
    #stags_codon4_TFIDF=["suggestedTag_codon4_TFIDF"]
    #stags_word=["suggestedTag_word"]
    #stags_word_TFIDF=["suggestedTag_word_TFIDF"]
    #stags_word2=["suggestedTag_word2"]
    #stags_suggested=["suggestedTag_resolved"]
    #prob_IN=["probabilityIN"]
    #prob_IN_rank=["probabilityINrank"]
    SVMsumVotes=["SVMsumVotes"]
    SVMnumVotes=["SVMnumVotes"]
    SVMmeanVote=["SVMmeanVote"]
    sAssignment=["SuggestedAssignment"]
    reviewT=["ReviewScreening_true"]
    reviewT_random=["ReviewScreening_random?"]
    reviewT_combined=["ReviewScreening_combined"]
    for article in articles:
        ids.append(article.ID)
        gtags.append(article.goldTag)
        gAssignment.append(article.goldAssignment)
        #stags_codon4.append(article.tag_nb_codon4)
        #stags_codon3.append(article.tag_nb_codon3)
        #stags_word.append(article.tag_nb_word)
        #stags_word_TFIDF.append(article.tag_nb_word_TFIDF)
        #stags_word2.append(article.tag_nb_word2)
        #stags_codon4_TFIDF.append(article.tag_nb_codon4_TFIDF)
        #stags_suggested.append(article.tag_suggested)
        abs.append(article.content)
        #prob_IN.append(article.prob_IN)
        #prob_IN_rank.append(article.prob_IN_rank)
        SVMsumVotes.append(article.SVMvote_sum)
        SVMnumVotes.append(article.SVMvote_count)
        SVMmeanVote.append(article.SVMvote_mean)
        sAssignment.append(article.SVMvote_decision)
        reviewT.append(article.SVM_recommendReview)
        reviewT_random.append(article.SVM_recommendReview_random)
        if article.SVM_recommendReview == True or article.SVM_recommendReview_random ==True:
            reviewT_combined.append(True)
        else:
            reviewT_combined.append(False)
    ##Create data columns and create key file.
    rowList=[ids,
        abs,
        gtags,
        gAssignment,
        #stags_codon4,
        #stags_codon3,
        #stags_codon4_TFIDF,
        #stags_word,
        #stags_word_TFIDF,
        #stags_word2,
        #stags_suggested,
        #prob_IN,
        #prob_IN_rank,
        SVMsumVotes,
        SVMnumVotes,
        SVMmeanVote,
        sAssignment,
        reviewT,
        reviewT_random,
        reviewT_combined]
    zipRowList=zip(*rowList)
    with open(str(int(startTime))+'_keyFile.csv', 'w', newline='',encoding="ISO-8859-1") as file:
        writer=csv.writer(file)
        writer.writerows(zipRowList)

    ##Create data columns and create suggestions file.
    rowList2=[ids,
        abs,
        gtags,
        gAssignment,
        #stags_codon4,
        #stags_codon3,
        #stags_codon4_TFIDF,
        #stags_word,
        #stags_word_TFIDF,
        #stags_word2,
        #stags_suggested,
        #prob_IN,
        #prob_IN_rank,
        #sAssignment,
        #reviewT,
        #reviewT_random,
        reviewT_combined]
    zipRowList2=zip(*rowList2)
    with open(str(int(startTime))+'_suggestionsFile.csv', 'w', newline='',encoding="ISO-8859-1") as file:
        writer=csv.writer(file)
        writer.writerows(zipRowList2)








#############################################################
##Import data and create data objects.

##Import articles and create an object containing them all.
inputArticles=createArticles()



##Handle duplicates and non-consistent tagging.
flagDuplicateArticles(inputArticles)
compareDupArticleTags(inputArticles)

##Randomly pick which articles will be used for optimising and training classifiers.
##If the trainProp is 0 then all of the minority aticle class will be used, matched
##to a subset of the majority class of equal size.
PickTrainingArticles(inputArticles,numClassifiers=numClassifiers,trainProp=trainProp)


##Create a SVMdata object from the inputArticles list. The vocabulary and data arrays
##will be created based on only the word/codon content of the articles that will be
##used for training.
SVMdata_full=createSVMdata(inputArticles,"word")

##Create a list of lists of the training abstract IDs for each classifier (usually two).
trainingIDgroups=CreateTrainingData(SVMdata_full,numClassifiers)




##############################################################
##Run C and gamma parameter optimisation.
paramsGrid=CreateInitialParams(range=initialParamRange)
print("paramsGrid: ",paramsGrid)

SVMparams=NestedParamsOptimisation(paramsGrid,SVMdata_full,trainingIDgroups,initialParamRange,nestedIterations=nestedIterations,refineRangeFactor=2)
print("SVMparams: ",SVMparams)








###########################################################
##Run classifier with the optimised parameters
print("Training Classifier with optimised parameters...")
#SVMparams={"C":10,"gamma":0.001}
RunClassifiers(SVMdata_full,trainingIDgroups,SVMparams,inputArticles)

##Ask the user how they would like their results.
print("\nClassifier ready for use.")
#desiredOutput=input("How do you want the results?\nReturn all articles with probability values (A)\nSpecify a desired number of results (B)\nDefined by a threshold of mimimum acceptible sensitivity (C)\n)
#if desiredOutput=="B" or desiredOutput=="b":
#    specifiedOutput=
AdjustThresholdForRecall(inputArticles,startingThreshold,minRecall)
#print("Optimised parameter values: ",SVMparams)


##########################################################
##Make review recommendations.
reccReviewNum=SVM_recommendReview(inputArticles)
##Make an equal number of review recommendations at random.
SVM_recommendReview_random(inputArticles,reccReviewNum)



#####################################################
#Export results.
exportRecommendations(inputArticles)

#############################################
#Print the size of the vocab.
print("vocabSize: ",len(SVMdata_full.Feature_names))

#####################################################
##Report on program runtime.
print("Program took",int(time.time()-startTime),"seconds to run.")

##Prompt to exit program.
input('Press ENTER to exit')
