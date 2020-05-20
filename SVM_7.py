##Program requires installatioon of SciKit from https://scikit-learn.org/stable/install.html
##Program demo can be found at https://www.datacamp.com/community/tutorials/svm-classification-scikit-learn-python

##Define the number of classifiers to be trained for the commitee
numClassifiers=2
##Define the proportion of eligiable abstracts to use for classifier training,
##(after correcting for class imbalance).
trainProp=1
##Define the threshold of votes required for inclusion (as a proportion of 1).
startingThreshold=0.5
##Define the minimum acceptible recall (sensitivity) for the overall classifier.
minRecall=0.8

# Import necessary packages.
import time
startTime = time.time()
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
from sklearn.datasets import load_iris
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import GridSearchCV

# Utility function to move the midpoint of a colormap to be around
# the values of interest.
class MidpointNormalize(Normalize):

    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

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
    Votes=list()
    def __init__(self,DESCR,IDs,Data,Feature_names,Filename,Target,Target_names):
        self.DESCR=DESCR
        self.IDs=IDs
        self.Data=Data
        self.Feature_names=Feature_names
        self.Filename=Filename
        self.Target=Target
        self.Target_names=Target_names
        #self.Votes=[[0]]*len(IDs)

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
        wordVector=[0]*len(Feature_names)
        ## For each word in the article word list set, change the value of the index
        ## equivalent to the Feature_names to 1. Ignore words that are not in Feature_names.
        ##The try/except blocks are to handle ignoring words that are not in the Feature_names,
        ##(i.e. not found in the articles selected to be the training set.)
        if dataUnits=="word":
            for word in article.contentWordListSet:
                try:
                    pos=Feature_names.index(word)
                    wordVector[pos]=1
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

##perform the SVM classifiication over a range of C and gamma values, returning
##the C, gamma, and fitted results.
def OptimiseParams(dataset,numClassifiers=2):
    print("Optimising parameters...")
    ##Find classifier performance over a range of parameter values.
    def FindParams(dataset,numClassifiers):

        ##define the training data
        #print("Total abstracts to classify: ",len(dataset.Target))
        #print("Proportion to use as training set in optimiser: ",optimisingProp)
        #totalAbstracts=len(dataset.Target)
        ##divide the trainProp by 2 to calculate the max number of each class (IN and EX).
        #maxAbstracts=int(totalAbstracts*optimisingProp/2)

        ##Create X (dimensions array)
        X=dataset.Data
        ##Create y (class array)
        y=dataset.Target

        ##make a list for INs and EXs
        #All_IN_data=list()
        #All_EX_data=list()
        #All_IN_target=list()
        #All_EX_target=list()
        #for i in range(0,len(y)):
        #    if y[i] == 0:
        #        All_EX_data.append(X[i])
        #        All_EX_target.append(y[i])
        #    if y[i] == 1:
        #        All_IN_data.append(X[i])
        #        All_IN_target.append(y[i])


        ##Truncate both lists if they are above that length
        #if len(All_EX_data)>maxAbstracts:
        #    del All_EX_data[maxAbstracts:]
        #if len(All_EX_target)>maxAbstracts:
        #    del All_EX_target[maxAbstracts:]
        #if len(All_IN_data)>maxAbstracts:
        #    del All_IN_data[maxAbstracts:]
        #if len(All_IN_target)>maxAbstracts:
        #    del All_IN_target[maxAbstracts:]

        #X2=All_EX_data+All_IN_data
        #y2=All_EX_target+All_IN_target
        #print(len(X2),"abstracts used for optimisation.")

        # Train classifiers
        #
        # For an initial search, a logarithmic grid with basis
        # 10 is often helpful. Using a basis of 2, a finer
        # tuning can be achieved but at a much higher cost.

        ##Define the search space for parameter optimisation.
        #C_range = np.logspace(-2, 10, 13)
        #gamma_range = np.logspace(-9, 3, 13)
        C_range = np.logspace(-2, 2, 5)
        gamma_range = np.logspace(-3, 1, 5)
        #C_range = np.logspace(-3, 3, 7)
        #gamma_range = np.logspace(-3, 3, 7)
        #C_range = np.logspace(-3, 11, 15)
        #gamma_range = np.logspace(-10, 4, 15)
        #C_range = np.logspace(-4, 12, 17)
        #gamma_range = np.logspace(-11, 5, 17)

        param_grid = dict(gamma=gamma_range, C=C_range)
        cv = StratifiedShuffleSplit(n_splits=5, train_size=(1/numClassifiers), random_state=42)

        runTime=time.time()
        grid = GridSearchCV(SVC(kernel='rbf'), param_grid=param_grid, cv=cv)
        grid.fit(X, y)
        print("Using RBF kernel, the best parameters are %s with a score of %0.2f"
              % (grid.best_params_, grid.best_score_))
        print("Parameter search took ",int(time.time()-runTime)," seconds.")

        #runTime=time.time()
        #grid = GridSearchCV(SVC(kernel='linear'), param_grid=param_grid, cv=cv)
        #grid.fit(X, y)
        #print("Using LINEAR kernel, the best parameters are %s with a score of %0.2f"
        #      % (grid.best_params_, grid.best_score_))
        #print("Parameter search took ",int(time.time()-runTime)," seconds.")

        #runTime=time.time()
        #grid = GridSearchCV(SVC(kernel='poly'), param_grid=param_grid, cv=cv)
        #grid.fit(X, y)
        #print("Using POLY kernel, the best parameters are %s with a score of %0.2f"
        #      % (grid.best_params_, grid.best_score_))
        #print("Parameter search took ",int(time.time()-runTime)," seconds.")

        #runTime=time.time()
        #grid = GridSearchCV(SVC(kernel='sigmoid'), param_grid=param_grid, cv=cv)
        #grid.fit(X, y)
        #print("Using SIGMOID kernel, the best parameters are %s with a score of %0.2f"
        #      % (grid.best_params_, grid.best_score_))
        #print("Parameter search took ",int(time.time()-runTime)," seconds.")


        return(grid,C_range,gamma_range)
    gridCrangeGammaRange=FindParams(dataset,numClassifiers)
    # draw visualization of parameter effects
    def VisualiseParameterEffects(gridCrangeGammaRange):
        grid=gridCrangeGammaRange[0]
        C_range=gridCrangeGammaRange[1]
        gamma_range=gridCrangeGammaRange[2]
        scores = grid.cv_results_['mean_test_score'].reshape(len(C_range),
                                                         len(gamma_range))
        # Draw heatmap of the validation accuracy as a function of gamma and C
        #
        # The score are encoded as colors with the hot colormap which varies from dark
        # red to bright yellow. As the most interesting scores are all located in the
        # 0.92 to 0.97 range we use a custom normalizer to set the mid-point to 0.92 so
        # as to make it easier to visualize the small variations of score values in the
        # interesting range while not brutally collapsing all the low score values to
        # the same color.

        plt.figure(figsize=(8, 6))
        plt.subplots_adjust(left=.2, right=0.95, bottom=0.15, top=0.95)
        plt.imshow(scores, interpolation='nearest', cmap=plt.cm.hot,
                   norm=MidpointNormalize(vmin=0.2, midpoint=0.92))
        plt.xlabel('gamma')
        plt.ylabel('C')
        plt.colorbar()
        plt.xticks(np.arange(len(gamma_range)), gamma_range, rotation=45)
        plt.yticks(np.arange(len(C_range)), C_range)
        plt.title('Validation accuracy')
        plt.savefig(
            "ParamsFig"+str(int(startTime))+".png"
        )
    VisualiseParameterEffects(gridCrangeGammaRange)
    return(gridCrangeGammaRange[0].best_params_)

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

##Perform the SVM classification on the data, using the C and gamma parameters
##chosen from the optimisation, and definining the training and testing data
## according the IDs output by the CreateTrainingData function.
def TrainClassifier(dataset,bestParams,trainingIDgroup):
    print("\nTraining classifier...")

    # Import train_test_split function.
    from sklearn.model_selection import train_test_split

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
    for pos in range(0,len(dataset.IDs)):
        ##If the ID at that position is in the training group list.
        if dataset.IDs[pos] in trainingIDgroup:
            ##Add the data vector to the training list.
            Xtrain.append(dataset.Data[pos])
            ##Add the assignment value to the training list.
            Ytrain.append(dataset.Target[pos])
        else:
            ##OTherwise add them to the testing lists.
            Xtest.append(dataset.Data[pos])
            Ytest.append(dataset.Target[pos])
            ##Make a list of the testing set IDs too, so that the votes can be
            ## assigned after predictions have been made
            YID.append(dataset.IDs[pos])
    #print("YID: ",YID)
    print("trainingIDgroup: ",trainingIDgroup)
    #print("Ytrain: ",Ytrain)
    #print("Ytest: ",Ytest)
    # Import svm model
    from sklearn import svm

    # Create a svm Classifier. Linear Kernel
    clf = svm.SVC(kernel='rbf',C=bestParams['C'],gamma=bestParams['gamma'],probability=True)

    #Train the model using the training sets
    clf.fit(Xtrain,Ytrain)

    #Predict the response for test dataset. This returns the probability of the
    ##sample for each class in the model. The columns correspond to the classes
    ##in sorted order, as they appear in the attribute classes_
    Yout = clf.predict_proba(Xtest)
    print("Yout: ",Yout)
    Ypred = list()
    for pos in Yout:
        Ypred.append(pos[1])
    print("Ypred: ",Ypred)



    ##convert the numpy object into a list.
    #Ypred=list()
    #for num in Yout:
    #    Ypred.append(num)

    print("Total number of IN assignments made by classifier: ",sum(Ypred))
    print("Total number of assignments made by classifier: ",len(Ypred))
    print("Propotion of IN assignments made by classifier: ",(sum(Ypred)/len(Ypred)))

    # Import scikit-learn metrics module for accuracy calculation
    from sklearn import metrics

    #print("Ytest: ",Ytest)
    #print("Ypred: ",Ypred)



    # Model Accuracy: how often is the classifier correct?
    #print("Accuracy: ",metrics.accuracy_score(Ytest,Ypred))

    # Model Precision: what percentage of positively labelled tuples are actually positive?
    #print("Precision: ",metrics.precision_score(Ytest,Ypred))

    #Model Recall: What percentage of positive tuples are labelled as positive?
    #print("Recall: ",metrics.recall_score(Ytest,Ypred))

    #Model Recall: What is the cohen's kappa score?
    #print("Kappa: ",metrics.cohen_kappa_score(Ytest,Ypred))

    ##Use the caclculateSensitivity function to calculate sensitivity.
    #print("Sensitivity: ",CalculateSensitivity(Ytest,Ypred))

    ##Use the calculateKappa function to calculate kappa.
    #kappa=calculateKappa(Ytest,Ypred)
    #print("Cohen's kappa: ",kappa)

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

##Use the results of the SVM voting to decide which articles can be marked as includes.
def CountSVMvotes(articles,threshold=0.5):
    print("\nCounting SVM votes...")
    for article in articles:
        article.SVMvote_mean=article.SVMvote_sum/article.SVMvote_count
        ##Use the threshold value to mark for include those articles with a high
        ##enough average vote.
        if article.SVMvote_mean>=threshold:
            article.SVMvote_decision=1
        #print(article.ID,article.SVMvote_sum,article.SVMvote_count,article.SVMvote_mean,article.SVMvote_decision)
    print("Votes counted.")

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

##Makes review recommendations at random, given a desired number.
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

def OptimiseParamsForRecall(trainingIDlistList,dataset,minRecall):
    ##Define a range of C values to test.
    C_range = np.logspace(-2, 2, 5)
    ##Define a range of gamma values to test.
    gamma_range = np.logspace(-3, 1, 5)

    ##Iterate over C_range.
    for Cval in C_range:
        ##Iterate over gamma_range.
        for Gval in gamma_range:
            ##create params dict object.
            currentParams={'C':Cval,'gamma':Gval}
            ##iterate over each training group.
            for group in trainingIDlistList:
                ##Train the classifier and tally up the votes.
                TrainClassifier(dataset,currentParams,group)
                curentThreshold=startingThreshold
                CountSVMvotes(inputArticles,threshold=currentThreshold)
                ## Calculate the metrics of the overall SVM INEX assignments.
                ##First create the goldList and testList.
                from sklearn import metrics
                inputGoldAssListBool=list()
                SVMassListBool=list()
                for article in inputArticles:
                    if article.goldAssignment=="IN":
                        inputGoldAssListBool.append(1)
                    else:
                        inputGoldAssListBool.append(0)
                    SVMassListBool.append(article.SVMvote_decision)
                ##Calculate kappa and Recall.
                currentRecall=metrics.recall_score(inputGoldAssListBool,SVMassListBool)
                currentKappa=metrics.cohen_kappa_score(inputGoldAssListBool,SVMassListBool)
                ##Increase threshold until minimum Recall is reached.
                while currentRecall<minRecall:
                    currentThreshold=currentThreshold-0.05
                    CountSVMvotes(inputArticles,threshold=currentThreshold)
                    ## Calculate the metrics of the overall SVM INEX assignments.
                    ##First create the goldList and testList.
                    from sklearn import metrics
                    inputGoldAssListBool=list()
                    SVMassListBool=list()
                    for article in inputArticles:
                        if article.goldAssignment=="IN":
                            inputGoldAssListBool.append(1)
                        else:
                            inputGoldAssListBool.append(0)
                        SVMassListBool.append(article.SVMvote_decision)
                    ##Calculate kappa and Recall.
                    currentRecall=metrics.recall_score(inputGoldAssListBool,SVMassListBool)
                    currentKappa=metrics.cohen_kappa_score(inputGoldAssListBool,SVMassListBool)
                ##Record the optimised kappa, recall, and threshold for this combination of gamma and C.
                print("currentParams: ",currentParams)
                print("currentRecall: ",currentRecall)
                print("currentKappa: ",currentKappa)
#################################################################


### Run the program

## Define punctuations to be removed from analysis.
punctuations = "_çìëá•™©!£$€/%^&*+±=()â‰¥[]|0123456789'=.,:;?%<>ÿòñ~#@-—–{}úøîæ÷ó¬åà®¯§"+'"“”'

##Import articles and create an object containing them all.
inputArticles=createArticles()

##Handle duplicates and non-consistent tagging.
flagDuplicateArticles(inputArticles)
compareDupArticleTags(inputArticles)
##Randomly pick which articles will be used for optimising and training classifiers.
PickTrainingArticles(inputArticles,numClassifiers=numClassifiers,trainProp=trainProp)

##Create a list of just the articles from inputArticle that have been selected as
## training articles.
trainingArticles=list()
for article in inputArticles:
    if article.SVMtrainIN==True or article.SVMtrainEX==True:
        trainingArticles.append(article)

##Create a SVMdata object from the inputArticles list. The vocabulary and data arrays
##will be created based on only the word/codon content of the articles that will be
##used for training.
FibratesData_full=createSVMdata(inputArticles,"word")

##Create a second SVM data object from the trainingArticles list. The vocabulary will
## be identical to the full Fibrates_data object.
FibratesData_train=createSVMdata(trainingArticles,"word")

##Optimise the classifier parameters using only the training articles.
#bestParams=OptimiseParams(FibratesData_train,numClassifiers=numClassifiers)




## Define 'bestParams' for the purpose of testing.
bestParams={'C': 1.0, 'gamma': 0.01}
print(bestParams)

##Create the lists of training data from SVM data object that only contains the
##training data.
trainingIDgroups=CreateTrainingData(FibratesData_train,numClassifiers=numClassifiers)
#print("trainingIDgroups: ",trainingIDgroups)

##Optimise the C and gamma parameters for a minimum recall that has specified.
OptimiseParamsForRecall()


##Use the trainingIDgroups to run the classifier, with the parameters from the
##parameter optimisation, on each group of the traing groups, and then to classify
##whichever articles are not in that particular group.
for group in trainingIDgroups:
    TrainClassifier(FibratesData_full,bestParams,group)

##Using the votes totals calculate the mean vote and apply the threshold for inclusion.
CountSVMvotes(inputArticles,threshold=votesThreshold)

## Calculate the metrics of the overall SVM INEX assignments.
##First create the goldList and testList.
from sklearn import metrics
inputGoldAssListBool=list()
SVMassListBool=list()
for article in inputArticles:
    if article.goldAssignment=="IN":
        inputGoldAssListBool.append(1)
    else:
        inputGoldAssListBool.append(0)
    SVMassListBool.append(article.SVMvote_decision)
#print(inputGoldAssListBool)
#print(SVMassListBool)

print("Overall Accuracy score: ",metrics.accuracy_score(inputGoldAssListBool,SVMassListBool))
print("Overall Recall: ",metrics.recall_score(inputGoldAssListBool,SVMassListBool))
print("Overall SVM kappa: ",metrics.cohen_kappa_score(inputGoldAssListBool,SVMassListBool))

##Make review recommendations.
reccReviewNum=SVM_recommendReview(inputArticles)
#for article in inputArticles:
#    print(article.ID,article.goldAssignment,article.SVMvote_decision,article.SVM_recommendReview)

##Make an equal number of review recommendations at random.
SVM_recommendReview_random(inputArticles,reccReviewNum)

##Export results.
exportRecommendations(inputArticles)

##Report on program runtime.
print("Program took",int(time.time()-startTime),"seconds to run.")

##Prompt to exit program.
input('Press ENTER to exit')
