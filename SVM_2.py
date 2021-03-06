##Program requires installatioon of SciKit from https://scikit-learn.org/stable/install.html
##Program demo can be found at https://www.datacamp.com/community/tutorials/svm-classification-scikit-learn-python

# Import necessary packages.
import time
startTime = time.time()
import math
import csv
import random
random.seed(1)

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
    ##SVM attributes
    SVMvote_sum=0
    SVMvote_count=0
    SVMvote_mean=0
    SVMvote_decision=0
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

##Using the data in the articles object, create an object for SVM data.
def createSVMdata(articles):
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
    obOut=SVMdata(DESCR,IDs,Data,Feature_names,Filename,Target,Target_names)
    return(obOut)


##perform the SVM classifiication over a range of C and gamma values, returning
##the C, gamma, and fitted results.
def OptimiseParams(dataset):
    ##Find classifier performance over a range of parameter values.
    def FindParams(dataset):
        ##Create X (dimensions array)
        X=dataset.Data
        ##Create y (class array)
        y=dataset.Target

        # Train classifiers
        #
        # For an initial search, a logarithmic grid with basis
        # 10 is often helpful. Using a basis of 2, a finer
        # tuning can be achieved but at a much higher cost.

        ##Define the search space for parameter optimisation.
        C_range = np.logspace(-2, 10, 13)
        gamma_range = np.logspace(-9, 3, 13)
        #C_range = np.logspace(-3, 3, 7)
        #gamma_range = np.logspace(-3, 3, 7)
        #C_range = np.logspace(-3, 11, 15)
        #gamma_range = np.logspace(-10, 4, 15)
        #C_range = np.logspace(-4, 12, 17)
        #gamma_range = np.logspace(-11, 5, 17)

        param_grid = dict(gamma=gamma_range, C=C_range)
        cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=42)

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
    gridCrangeGammaRange=FindParams(dataset)
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

## using the total dataset and defining a desired number of classifiers, this
## function outputs two lists of IDS, one for in abstracts and one for ex abstracts,
## with sublists equal in number to the desired number of classifiers. The function
## randomly divides up whichever the smaller class is (usually includes), into equal length
## sublists. These are then matched by a subset of the EX IDs. The sublists are all the
## same length, and any 'excess' abstracts IDs are discarded. They are returned as
## a list of lists, with EX IDs in the 0 position, IN ID's in the 1 position.
def CreateTrainingData(dataset,numClassifiers=10):


    ##Create a list for all IN IDs and one for all EX IDs
    AllIDs_IN=list()
    AllIDs_EX=list()
    ##ADD the IDs for all  input articles to their respectie list.
    for pos in range(0,len(dataset.Target)):
        if dataset.Target[pos]==1:
            AllIDs_IN.append(dataset.IDs[pos])
        else:
            AllIDs_EX.append(dataset.IDs[pos])

    ##Print the lists to check them.
    #for pos in range(0,len(FibratesData.Target)):
    #    print(FibratesData.Target[pos])
    #    print(FibratesData.IDs[pos])
    #print(AllIDs_IN)
    #print(AllIDs_EX)

    ##Define the number of abstracts in the smaller class.
    numInSmallerClass=0
    INexcess=len(AllIDs_IN)-len(AllIDs_EX)
    if INexcess >=0:
        numInSmallerClass=len(AllIDs_EX)
    if INexcess <0:
        numInSmallerClass=len(AllIDs_IN)

    ##Check there are enough abstracts in the smaller class for at least one
    ## Per classifier.
    if numInSmallerClass<numClassifiers:
        print("\nNot enough abstracts in minority class to train",numClassifiers,"classifiers.")
        print("Reducing the number of classifiers to" ,numInSmallerClass,".\n")
        numClassifiers=numInSmallerClass

    ##Randomise the include and exclude ID lists.
    random.shuffle(AllIDs_IN)
    random.shuffle(AllIDs_EX)
    ##Truncated the EX list so that it is the same length as the IN list.
    AllIDs_EX=AllIDs_EX[:len(AllIDs_IN)]

    ##Define how many pairs of INEX abstract pairs will be fed for training into each
    ## classifier.
    print("numClassifiers: ",numClassifiers)
    absPerClassifier=len(AllIDs_IN)//numClassifiers
    print("absPerClassifier: ",absPerClassifier)
    ##create include ID list sublists of the correct length to yield the same number
    ##of sublists are there are desired classifiers.
    INIDs_rand=list()
    EXIDs_rand=list()
    for i in range(0,len(AllIDs_IN), absPerClassifier):
        INIDs_rand.append(AllIDs_IN[i:i+absPerClassifier])
        EXIDs_rand.append(AllIDs_EX[i:i+absPerClassifier])

    #print("shuffled, paired INEX training lists")
    print(INIDs_rand)
    print(EXIDs_rand)


    ## Remove the last sublist if it is not full.
    if len(INIDs_rand)>numClassifiers:
        del INIDs_rand[-1]
        del EXIDs_rand[-1]

    #print("shuffled, paired INEX training lists")
    print(INIDs_rand)
    print(EXIDs_rand)

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

    # Import svm model
    from sklearn import svm

    # Create a svm Classifier. Linear Kernel
    clf = svm.SVC(kernel='rbf',C=bestParams['C'],gamma=bestParams['gamma'])

    #Train the model using the training sets
    clf.fit(Xtrain,Ytrain)

    #Predict the response for test dataset
    Yout = clf.predict(Xtest)
    ##convert the numpy object into a list.
    Ypred=list()
    for num in Yout:
        Ypred.append(num)

    # Import scikit-learn metrics module for accuracy calculation
    from sklearn import metrics

    print("Ytest: ",Ytest)
    print("Ypred: ",Ypred)



    # Model Accuracy: how often is the classifier correct?
    print("Accuracy: ",metrics.accuracy_score(Ytest,Ypred))

    # Model Precision: what percentage of positively labelled tuples are actually positive?
    print("Precision: ",metrics.precision_score(Ytest,Ypred))

    #Model Recall: What percentage of positive tuples are labelled as positive?
    print("Recall: ",metrics.recall_score(Ytest,Ypred))

    ##Use the calculateKappa function to calculate kappa.
    kappa=calculateKappa(Ytest,Ypred)
    print("Cohen's kappa: ",kappa)

    ##For each of the testing abstracts, place the vote back into the original
    ## articles object.
    for article in trainingArticles:
        for pos in range(0,len(Ypred)):
            #print("Current article ID: ",article.ID)
            if article.ID == YID[pos]:
                #print("Article ID matches the Ytest list at this position")
                #print("Vote added for article ID",YID[pos],":",Ypred[pos])
                article.SVMvote_sum=article.SVMvote_sum+Ypred[pos]
                article.SVMvote_count=article.SVMvote_count+1
                #temp=FibratesData.IDs.index(YID[pos])
                #FibratesData.Votes[temp].append(Ypred[pos])

##Caclulate Cohen's kappa coefficient between two lists of strings.
def calculateKappa(rList,cList):
    ##Define variables
    agreeList=list()
    randAgreeProb=0
    tagsKey=list()
    rDict=dict()
    cDict=dict()
    randAgreeDict=dict()
    kappa=0
    ##Calculate raw agreement proportion.
    for pos in range(0,len(rList)):
        if rList[pos]==cList[pos]:
            agreeList.append(1)
        else:
            agreeList.append(0)
    agreeVal=sum(agreeList)/len(rList)
    ##Populate the tags key.
    for pos in rList:
        tagsKey.append(pos)
    for pos in cList:
        tagsKey.append(pos)
    tagsKey=set(tagsKey)
    ##Create a dictionary for the reference list and comparator list,
    ##containing the count for each tag.
    for tag in tagsKey:
        rDict[tag]=0
        cDict[tag]=0
    ##Populate the dictionaries with counts of tags.
    for pos in rList:
        rDict[pos]=rDict[pos]+1
    for pos in cList:
        cDict[pos]=cDict[pos]+1
    ##convert those tags into proportions
    for pos in rDict:
        rDict[pos]=rDict[pos]/(len(rList))
    for pos in cDict:
        cDict[pos]=cDict[pos]/(len(rList))
    ##Calculate chance of random agreement for each tag.
    for tag in tagsKey:
        #print("tag:", tag,rDict[tag],cDict[tag])
        randAgreeDict[tag]=rDict[tag]*cDict[tag]
    ##calculate overall probability of agreement by chance.
    for tag in randAgreeDict:
        randAgreeProb=randAgreeProb+randAgreeDict[tag]
    ##Calculate Kappa
    kappa=(agreeVal-randAgreeProb)/(1-randAgreeProb)
    #print("agreeVal: ",agreeVal)
    #print("randAgreeProb: ",randAgreeProb)
    #print("Kappa: ",kappa)
    return(kappa)

##Use the results of the SVM voting to decide which articles can be marked as includes.
def CountSVMvotes(articles,threshold=0.5):
    print("Counting SVM votes...")
    for article in trainingArticles:
        article.SVMvote_mean=article.SVMvote_sum/article.SVMvote_count
        ##Use the threshold value to mark for include those articles with a high
        ##enough average vote.
        if article.SVMvote_mean>=threshold:
            article.SVMvote_decision=1
        #print(article.ID,article.SVMvote_sum,article.SVMvote_count,article.SVMvote_mean,article.SVMvote_decision)

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

##Train Train classifiers.
bestParams=OptimiseParams(FibratesData)
print(bestParams)

##Create the lists of training data.
trainingIDgroups=CreateTrainingData(FibratesData,numClassifiers=10)
print("trainingIDgroups: ",trainingIDgroups)

##Use the trainingIDgroups to run the classifier, with the parameters from the
##parameter optimisation, on each group of the traing groups, and then to classify
##whichever articles are not in that particular group.
for group in trainingIDgroups:
    TrainClassifier(FibratesData,bestParams,group)

CountSVMvotes(trainingArticles,threshold=0.5)
#print(FibratesData.Votes)

##Calculate the overall kappa for the SVM method after the votes have been tallied.
SVMincludes=list()
for article in trainingArticles:
    SVMincludes.append(article.SVMvote_decision)
goldIncludes=FibratesData.Target

overallKappa=calculateKappa(SVMincludes,goldIncludes)
print("Overall SVM kappa: ",overallKappa)

##Report on program runtime.
print("Program took",int(time.time()-startTime),"seconds to run.")

##Prompt to exit program.
input('Press ENTER to exit')
