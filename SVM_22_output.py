##Program requires installatioon of SciKit from https://scikit-learn.org/stable/install.html
##Program demo can be found at https://www.datacamp.com/community/tutorials/svm-classification-scikit-learn-python

##Input the starting parameters for running the classifier.
##Define the number of classifiers to be trained for the commitee. Published
##research suggests that 2 is usually optimal.
numClassifiers=2

##Define the proportion of eligiable abstracts to use for classifier training,
##(after correcting for class imbalance). This can be reduced from 1 if there
##is a particularly large dataset, and will train the classifier with a subset of
##the data.
trainProp=1

##Define an absolute maximum number of abstracts used for training. This will be independent
##of the trainProp value, and will be applied after it.
maxTrainingAbstracts=1000

##Define the threshold of mean classifier vote required for inclusion (as a proportion of 1).
##Increasing this value will increase the recall, but may decrease the Cohen's Kappa. This
##value is used as a starting point for the paramter optimisation.
startingThreshold=2.5

##Define the minimum acceptible recall (sensitivity) for the overall classifier.
##The higher this value the greater the sensitivity the final classifier will have,
##at the expense of accuracy and Kappa. Setting the minRecall to 0 will result in
##parameters that are optimised just based on Kappa scores.
minRecall=0.8

##define initial log parameter range. This will define the search grid area for the
##iniital C and gamma parameter search, as well as the scaling of refining searches.
initialParamRange=3

##Define how many iterations of the C and gamma parameter optimiser we want.
nestedIterations=1

## Define punctuations to be removed from abstract text before analysis.
punctuations = "_çìëá•™©!£$€/%^&*+±=()â‰¥[]|0123456789'=.,:;?%<>ÿòñ~#@-—–{}úøîæ÷ó¬åà®¯§"+'"“”'

##set randomseed value
randSeed=7

##Define how many suggestions to return
numReturn=100

##############################################################

# Import necessary packages.
import time
import math
import csv
import random
##Set a random seed for reproducability.
random.seed(randSeed)

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
##Create the program classes.

##Define a class for the article data, in the form that the sklearn SVM functions
##requires their input. In general this is in the form of lists where each index
##corresponds to each article.
class SVMdata:
    ##Define the basic data.
    ID_all=list()
    content_all=list()
    assignment_all=list()
    ID_train=list()

    ##Define the processed data.
    ##define a boolean list, 0 for testing set, 1 for training set.
    test_train=list()
    ##Data is a list of lists. for each article it contains a 1 or 0 for presence
    ##of each word in the vocabulary..
    Data=list()
    ##Feature_names is the vocabularly that corresponds to the boolean vectors.
    Feature_names=list()
    ##Target is the list of boolean values of 0=EX, 1=IN.
    Target=list()
    ##Target names is the list of assignment names (i.e. "EX" and "IN")

    ##Define the lists to store the results of classifiers.
    SVMvote_sum=list()
    SVMvote_count=list()
    SVMvote_mean=list()
    SVMvote_decision=list()
    SVM_recommendReview=list()
    SVM_recommendReview_random=list()

    ##Define the initialisation processing.
    Target_names=list()
    def __init__(self,ID_all,content_all,assignment_all,ID_train):
        ##assign the basic data.
        self.ID_all=ID_all
        self.content_all=content_all
        self.assignment_all=assignment_all
        self.ID_train=ID_train
        ##Create a boolean list for testing vs training articles.
        for id in self.ID_all:
                if id in self.ID_train:
                    self.test_train.append(1)
                else:
                    self.test_train.append(0)
        ##Define the Target attribute (the assignments)
        self.Target=self.assignment_all
        ##Define the names of the targets (e.g. 0="EX", 1="IN")
        self.Target_names=["EX","IN"]
        ##Define the Feature_names. This is the vocabulary. it is defined only using
        ##words from the training articles.
        for i in range(0,len(content_all)):
            if self.test_train[i]==1:
                for word in self.content_all[i]:
                    self.Feature_names.append(word)
        self.Feature_names=list(set(self.Feature_names))
        self.Feature_names.sort()
        ##Define the data for each article, as to whether each of the words in
        ##the vocabulary (Feature_names) is present or absent.
        for i in range (0,len(ID_all)):
            ##First create a vector of Falses equal in length to the voculary.
            wordVector=[False for i in range(0,len(self.Feature_names))]
            ##Then change to True any positions where that Feature is present in
            ##the current article.
            for word in self.content_all[i]:
                try:
                    ##find the index for that word in the Feature_names.
                    pos=self.Feature_names.index(word)
                    ##Use that index to change that value in the wordVector to True.
                    wordVector[pos]=True
                except:
                    continue
            self.Data.append(wordVector)
        ##set all the SVM classifier lists to lists of 0.
        self.SVMvote_sum=[0 for i in range(0,len(self.ID_all))]
        self.SVMvote_count=[0 for i in range(0,len(self.ID_all))]
        self.SVMvote_mean=[0 for i in range(0,len(self.ID_all))]
        self.SVMvote_decision=[0 for i in range(0,len(self.ID_all))]
        self.SVMvote_recommendReview=[0 for i in range(0,len(self.ID_all))]
        self.SVM_recommendReview_random=[0 for i in range(0,len(self.ID_all))]
        #print("length ID_all: ",len(self.ID_all))
        #print("length SVMvote_sum: ",len(self.SVMvote_sum))
##############################################################
## Define the program functions.

## Create an object containing all articles + create the word codons.
def createData():
    ## Ask user to input the file to import and which columns within it are which.
    trainFile=input('Please enter the csv filename (including ".csv"), then press ENTER: ')
    inputColID=input('Please enter the column letter containing abstract the IDs, then press Enter: ')
    inputColAbstract=input('Please enter the column letter containing the abstracts text, then press Enter: ')
    inputColGoldAssignment=input('Please enter the column letter containing the gold-standard IN-EX assignments, then press Enter: ')
    if trainFile is "":
        trainFile = "SVMTrainTiny.csv"
    if inputColID is "":
        inputColID = "A"
    inputColID=ord(inputColID.lower())-97
    if inputColAbstract is "":
        inputColAbstract = "B"
    inputColAbstract=ord(inputColAbstract.lower())-97
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
            goldAssignment=[]
            ##populate the empty lists with column data by row
            for row in readCSV:
                trainingIDlist.append(row[inputColID])
                contents.append(row[inputColAbstract])
                goldAssignment.append(row[inputColGoldAssignment])
    except:
        print("Unable to open file. Please check filename and type.")
        input('Press ENTER to exit')
        quit()
    ##remove the first item from the list for abstracts and screening codes
    ##as this is just the column names
    contents=contents[1:]
    trainingIDlist=trainingIDlist[1:]
    goldAssignment=goldAssignment[1:]
    ##Replace EX and IN with 0 and 1 in the goldAssignment.
    goldAssignmentBool=list()
    for i in goldAssignment:
        if i=="IN":
            goldAssignmentBool.append(1)
        else:
            goldAssignmentBool.append(0)
    ## Create an Article object for each article and store them in an object.
    return(trainingIDlist,contents,goldAssignmentBool)

##Process the article abstract content to be a list of the set of lowercase words
##without punctuation.
def Wordify(contentList):
    processedContentList=list()
    for content in contentList:
        w=""
        for character in content:
            if character not in punctuations:
                w=w+character
        w=w.lower()
        w=w.split()
        setList=list()
        for word in w:
            setList.append(word)
        setList=list(set(setList))
        processedContentList.append(setList)
    return(processedContentList)

## Create a list of the article that will be used as the training set
## for both SVM paramter optimisation and actual classification.
##There must be an equal number of INs and EXs to avoid class imbalance.
##There must be a number equal to the training proportion specified.
##There total number of training articles must not exceed the limit specified.
##There must be a number that can be divided equally into the number of classifiers
##specified.
def PickTrainingArticles(inputDataLists,randSeed):
    random.seed(randSeed)
    ##define lists contain the IDs of the articles of each class
    INlist=list()
    EXlist=list()
    ##count up the articles for each class.
    for i in range(0,len(inputDataLists[0])):
        if inputDataLists[2][i]==1:
            INlist.append(inputDataLists[0][i])
        else:
            EXlist.append(inputDataLists[0][i])
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
    ##Reduce the size of the training lists if they sum to be greater than the
    ##maxTrainingAbstracts.
    print("Reducing the size of the training sets to lie below the absolute maximum.")
    print("Defined maximum number is: ",maxTrainingAbstracts)
    print("Current number is: ",(len(INlist)+len(EXlist)))
    if len(INlist)>(maxTrainingAbstracts/2):
        print("Reducing size of training set...")
        del INlist[int(maxTrainingAbstracts/2):]
        del EXlist[int(maxTrainingAbstracts/2):]
    print("number of IN articles in dataset: ",len(INlist))
    print("number of EX articles in dataset: ",len(EXlist))
    ##Reduce the size of the training lists so that they can be evenly split by
    ##the number of classifiers.
    print("Reducing the size of training sets to match classifier training set size.")
    print("Defined number of classifiers is: ", numClassifiers)
    reduceByClassifierNum=int(len(INlist)%(numClassifiers))
    del EXlist[len(EXlist)-reduceByClassifierNum:]
    del INlist[len(INlist)-reduceByClassifierNum:]
    print("number of IN articles in dataset: ",len(INlist))
    print("number of EX articles in dataset: ",len(EXlist))
    ##Combine the INlist and EXlist and return the combined list.
    return(EXlist+INlist)

##Create a list of lists on the training data sets. I.e. if there are 3 classifiers
## this returns a list of three lists of equal length and matched IN and EX exemplars.
def CreateTrainingIDsLists(trainingIDlist,randSeed):
    random.seed(randSeed)
    ##Split the list back into INs and EXs.
    EXlist=trainingIDlist[:int(len(trainingIDlist)/2)]
    INlist=trainingIDlist[int(len(trainingIDlist)/2):]
    #print("EXList: ",EXlist)
    #print("INlist: ",INlist)
    ##create the sublists.
    EXlistSub=list()
    INlistSub=list()
    absPerClassifier=int(len(EXlist)/numClassifiers)
    #print("absPerClassifier: ",absPerClassifier)
    for i in range(0,len(EXlist),absPerClassifier):
        EXlistSub.append(EXlist[i:i+absPerClassifier])
        INlistSub.append(INlist[i:i+absPerClassifier])
    #print("EXlistSub: ",EXlistSub)
    #print("INlistSub: ",INlistSub)
    ##Merge the in and EX lists pairwise.
    IDgroups=list()
    for pos in range(0,len(EXlistSub)):
        IDgroups.append(EXlistSub[pos]+INlistSub[pos])
    #print("IDgroups: ",IDgroups)
    ## Return the list of ID number groups.
    return(IDgroups)

##Create inital C parameter for optimisation. This will output a list
##of dictionaries, each with 3 C parameter values.
## the range argument will give the number of orders of magnitude the values will span.
def CreateInitialParams(range=10):
    ##Define a list of real numbers to use as exponents
    expValues=[-1-(range/2),-1,-1+(range/2)]
    ##Use these as exponents for a log scale.
    paramValues=list()
    for val in expValues:
        paramValues.append(10**val)
    print("paramValues :",paramValues)
    ##create a dictionary holding all combinations of C and gamma values based on
    ##the three values.
    paramsGrid=list()
    for val1 in paramValues:
        print({"C":val1})
        paramsGrid.append({"C":val1})
    return(paramsGrid)

##Input is a dictionary of a C and gamma parameter values. The funtion takes these
##values, along with a range argument to output a new 3x3 grid of parameters for
##optimisation.
def UpdateParamsGrid(optParams,range=5):
    ##pull out the parameter values.
    Copt=optParams["C"]
    #print("Copt: ",Copt)
    ## take the log of these values
    Copt=math.log(Copt,10)
    #print("Copt: ",Copt)
    ##define a range of expValues for each parameter.
    CexpValues=[Copt-(range/2),Copt,Copt+(range/2)]
    ##Use these as exponents for a log scale.
    CNewParamValues=list()
    for val in CexpValues:
        CNewParamValues.append(10**val)
    #print("paramValues :",paramValues)
    ##create a dictionary holding all combinations of C and gamma values based on
    ##the three values.
    paramsGrid=list()
    for val1 in CNewParamValues:
            #print({"C":val1})
            paramsGrid.append({"C":val1})
    return(paramsGrid)

##Train and test a classifier with a single training group, Adding class probabilities
##to the articles class data.
def RunClassifier(SVMdata,trainingIDgroup,param):
    print("\nTraining classifier...")

    ##Create a list each for the Data (words vector) and Target (assingment vector)
    ## for the test and train IDs.
    Xtrain=list()
    Ytrain=list()
    Xtest=list()
    Ytest=list()
    IDtest=list()
    ##Add the data from the dataset to either the training or testing XY sets
    ##based on whether they appear in the trainingIDgroup that has been passed
    ##to the function.
    ##For each position in the IDs list.
    for pos in range(0,len(SVMdata.ID_all)):
        ##If the ID at that position is in the training group list.
        if SVMdata.ID_all[pos] in trainingIDgroup:
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
            IDtest.append(SVMdata.ID_all[pos])
    #print("IDtest: ",IDtest)
    #print("trainingIDgroup: ",trainingIDgroup)
    #print("Ytrain: ",Ytrain)
    #print("Ytest: ",Ytest)
    # Import svm model
    from sklearn import svm

    # Create a svm Classifier. Linear Kernel
    clf = svm.LinearSVC(C=param["C"],random_state=7)

    #Train the model using the training sets
    clf.fit(Xtrain,Ytrain)

    ##Sparcify the model.
    print("Sparsifying model...")
    clf.sparsify()
    #Predict the response for test dataset. This returns the probability of the
    ##sample for each class in the model. The columns correspond to the classes
    ##in sorted order, as they appear in the attribute classes_
    for i in range(0,len(Xtest)):
        Yout=clf.decision_function([Xtest[i]])
        ##take 10 to the power of the decision_function output so that the values
        ## are all greater than 0.
        Yout=float(Yout)
        #print("Yout: ",Yout)
        Ypred=10**Yout
        #print("Ypred: ",Ypred)
        #place that score into the correct position in the SVM_sum list.
        ##Use the current Ytest index to find the article ID.
        YpredID=IDtest[i]
        ##Then use that article ID to find the index for that article in all
        ## the article IDs.
        IDindex=SVMdata.ID_all.index(YpredID)
        ##Then add the Ypred value to the SVMvote_sum at that index.
        SVMdata.SVMvote_sum[IDindex]=SVMdata.SVMvote_sum[IDindex]+Ypred
        ##Also add 1 to the vote count at the same index.
        SVMdata.SVMvote_count[IDindex]=SVMdata.SVMvote_count[IDindex]+1

## using the SVM dataset, the defined training ID groups, and input parameters for
## C, run the pre-determined number of classifiers and place the probability
## Results back into the SVM data object.
def RunClassifiers(SVMdata,trainingIDgroups,param):
    ##First remove any previous classifier probabilities.
    for pos in range(0,len(SVMdata.SVMvote_sum)):
        SVMdata.SVMvote_sum[pos]=0
        SVMdata.SVMvote_count[pos]=0
        SVMdata.SVMvote_mean[pos]=0
        SVMdata.SVMvote_decision[pos]=0



    for group in trainingIDgroups:
        RunClassifier(SVMdata,group,param)
    ##Finally, calculate the mean votes currently present for each article.
    for pos in range(0,len(SVMdata.SVMvote_mean)):
        SVMdata.SVMvote_mean[pos]=SVMdata.SVMvote_sum[pos]/SVMdata.SVMvote_count[pos]
    #print("INTER-RESULTS2")
    #print(SVMdata.SVMvote_sum)
    #print(SVMdata.SVMvote_count)
    #print(SVMdata.SVMvote_mean)
    #print(SVMdata.SVMvote_decision)

##USe the mean probabiltiy values already calculated and stored inside the articles
##object to calculate the kappa for a range of threshold values.
def AdjustThresholdForKappa(SVMdata,startingThreshold):
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
        for i in range(0,len(SVMdata.SVMvote_mean)):
            if SVMdata.SVMvote_mean[i]>=currentThreshold:
                SVMdata.SVMvote_decision[i]=1
                currentIN+=1
            else:
                SVMdata.SVMvote_decision[i]=0
                currentEX+=1
        ##Calculate the current proprotion included.
        currentINprop=currentIN/(currentIN+currentEX)
        ##Calculate the Recall and kappa
        inputGoldAssListBool=list()
        SVMassListBool=list()
        for i in range(0,len(SVMdata.SVMvote_mean)):
            if SVMdata.assignment_all[i]==1:
                inputGoldAssListBool.append(1)
            else:
                inputGoldAssListBool.append(0)
            SVMassListBool.append(SVMdata.SVMvote_decision[i])
        #print("inputGoldAssListBool: ",inputGoldAssListBool)
        #print("SVMassListBool: ",SVMassListBool)
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
        currentThreshold=currentThreshold*0.99
    ##Now apply the optimsised threshold value. This is only necessary for the
    ## final classifier, but shouldn't add much to runtime to do each time.
    for i in range(0,len(SVMdata.SVMvote_mean)):
        if SVMdata.SVMvote_mean[i]>=bestThreshold:
            SVMdata.SVMvote_decision[i]=1
        else:
            SVMdata.SVMvote_decision[i]=0

    ##Now print the best kappa and recall combination and the threshold that gave it.
    print("Final recall: ",bestRecall)
    print("Final Kappa: ", bestKappa)
    print("Final Threshold: ",bestThreshold)
    return({"Recall":bestRecall,"Kappa":bestKappa,"Threshold":bestThreshold})

##USe the mean probabiltiy values already calculated and stored inside the articles
##object to calculate the recall and then adjust the threshold until the recall is
##above the specified minimum.
def AdjustThresholdForRecall(SVMdata,startingThreshold,minRecall):
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
        for i in range(0,len(SVMdata.SVMvote_mean)):
            if SVMdata.SVMvote_mean[i]>=currentThreshold:
                SVMdata.SVMvote_decision[i]=1
            else:
                SVMdata.SVMvote_decision[i]=0
        ##Calculate the Recall and kappa
        inputGoldAssListBool=list()
        SVMassListBool=list()
        for i in range(0,len(SVMdata.SVMvote_mean)):
            if SVMdata.assignment_all[i]==1:
                inputGoldAssListBool.append(1)
            else:
                inputGoldAssListBool.append(0)
            SVMassListBool.append(SVMdata.SVMvote_decision[i])
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
        currentThreshold=currentThreshold*0.99

    ##Now apply the optimsised threshold value. This is only necessary for the
    ## final classifier, but shouldn't add much to runtime to do each time.
    for i in range(0,len(SVMdata.SVMvote_mean)):
        if SVMdata.SVMvote_mean[i]>=bestThreshold:
            SVMdata.SVMvote_decision[i]=1
        else:
            SVMdata.SVMvote_decision[i]=0

    ##Now print the best kappa and recall combination and the threshold that gave it.
    print("Final recall: ",bestRecall)
    print("Final Kappa: ", bestKappa)
    print("Final Threshold: ",bestThreshold)
    return({"Recall":bestRecall,"Kappa":bestKappa,"Threshold":bestThreshold})

## Run optimiser. This takes a list of 3 parameter combinations (C and gamma), along
## with the SVM data object and a list of training group IDs, and returns the
## C and gamma combination that gave the highest kappa once the results were thresholded
## for minimum recall.
def TripleParamsOptimiser(params,SVMdata,trainingIDgroups):
    ##run each set of parameters through the classifier and adjust for recall.
    for param in params:
        RunClassifiers(SVMdata,trainingIDgroups,param)
        SVMmetrics=AdjustThresholdForKappa(SVMdata,startingThreshold)
        param.update(SVMmetrics)
        print(params)
    ##pull out the C value from the dictionary with the highest kappa.
    kappaList=list()
    for paramcomb in params:
        kappaList.append(paramcomb["Kappa"])
    print("kappaList: ",kappaList)
    indexMaxKappa=kappaList.index(max(kappaList))
    print(indexMaxKappa)
    bestParams={"C":params[indexMaxKappa]["C"]}
    print("bestParams: ",bestParams)
    return(bestParams)

##takes grid of C and gamma parameters, runs the optimiser, then takes the optimal pair
##of parameters, generates a new smaller grid around them and runs the optimiser again.
##This repeats the specified number of times given as nestedIterations, refinine the
##log range by the factor given by refineRangeFactor each time.
def NestedParamsOptimisation(params,SVMdata,trainingIDgroups,initialParamRange,nestedIterations=3,refineRangeFactor=2):
    count = 0
    while count<nestedIterations:
        count=count+1
        print("Round ",count," of ",nestedIterations," in nested parameter optimisation...")
        optParams=TripleParamsOptimiser(params,SVMdata,trainingIDgroups)
        print("OptParams",optParams)

        params=UpdateParamsGrid(optParams,range=(initialParamRange/(refineRangeFactor**count)))
        print("UpdatedParams: ",params)
    return(optParams)

##Based on the current SVMvote_decision and the goldAssignment of each article in
##inputArticles, recommend those that are gold EX and voted as IN for further human
##review.
def SVM_recommendReview(SVMdata):
    print("Recommending articles for review...")
    k=0
    for i in range(0,len(SVMdata.ID_all)):
        #print(i)
        if SVMdata.assignment_all[i]==0 and SVMdata.SVMvote_decision[i]==1:
            SVMdata.SVMvote_recommendReview[i]=1
            k+=1
    print("Number of articles recommended for review: ",k)
    return(k)

##Makes review recommendations at random (of gold-standard Excludes), given a desired number.
def SVM_recommendReview_random(SVMdata,numReturn):
    print("Making random recommendations...")
    ##First set all random recommended reviews to False.
    for i in range(0,len(SVMdata.ID_all)):
        SVMdata.SVM_recommendReview_random[i]=0
    ##Now assign True values to the appropriate number of articles.
    countArticle=len(SVMdata.ID_all)
    posList=list()
    while len(posList)<numReturn:
        value=random.randint(0,countArticle-1)
        if SVMdata.SVM_recommendReview_random[value]==0 and SVMdata.assignment_all[value]==0:
            SVMdata.SVM_recommendReview_random[value]=1
            posList.append(value)
    print("Number of random review recommendations made: ",len(posList))

##Export t the results of the classifier into two files. The first contains just
##which articles have been recommended for review. The other contains the key as
##to which of those recommendations are based on the analysis or made at random.
def exportRecommendations(SVMdata):
    print("Exporting suggested tag results...")
    ids=["ID"]
    abs=["AbstractText"]
    gtags=["GoldTag"]
    gAssignment=["GoldAssignment"]
    SVMsumVotes=["SVMsumVotes"]
    SVMnumVotes=["SVMnumVotes"]
    SVMmeanVote=["SVMmeanVote"]
    sAssignment=["SuggestedAssignment"]
    reviewT=["ReviewScreening_true"]
    reviewT_random=["ReviewScreening_random?"]
    reviewT_combined=["ReviewScreening_combined"]
    for i in range(0,len(SVMdata.ID_all)):
        ids.append(SVMdata.ID_all[i])
        #gtags.append(SVMdata.gtags_all[i])
        gAssignment.append(SVMdata.assignment_all[i])
        abs.append(SVMdata.content_all[i])
        SVMsumVotes.append(SVMdata.SVMvote_sum[i])
        SVMnumVotes.append(SVMdata.SVMvote_count[i])
        SVMmeanVote.append(SVMdata.SVMvote_mean[i])
        sAssignment.append(SVMdata.SVMvote_decision[i])
        reviewT.append(SVMdata.SVMvote_recommendReview[i])
        reviewT_random.append(SVMdata.SVM_recommendReview_random[i])
        if SVMdata.SVMvote_recommendReview[i] == 1 or SVMdata.SVM_recommendReview_random[i] ==1:
            reviewT_combined.append(1)
        else:
            reviewT_combined.append(0)
    ##Create data columns and create key file.
    rowList=[ids,
        abs,
        #gtags,
        gAssignment,
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
        #gtags,
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










##############################################################

##Import the data as .csv.
##Process the data into a list of IDs, a list of Abstract text, a list of assignments.
inputDataLists=createData()
#for i in inputDataLists:
#    print(i)

##Process the article content to be a set list of lowercase words without punctuation.
wordsSetList=Wordify(inputDataLists[1])
#for i in wordsSetList:
#    print("NEXT")
#    print(i)

##Pick the articles to be used for training and testing.
trainingIDlist=PickTrainingArticles(inputDataLists,randSeed)
#print(trainingIDlist)

##Create a list of lists of the training abstract IDs for each classifier (usually two).
trainingIDgroups=CreateTrainingIDsLists(trainingIDlist,randSeed)


##Create the SVM data object.
SVMdata=SVMdata(inputDataLists[0],wordsSetList,inputDataLists[2],trainingIDlist)
#print(SVMdata.ID_all)
#print(SVMdata.content_all)
#print(SVMdata.assignment_all)
#print(SVMdata.ID_train)
#print(SVMdata.test_train)
#print(SVMdata.Target)
#print(SVMdata.Target_names)
#print(SVMdata.Feature_names)
#print(SVMdata.Data)
#print(SVMdata.SVMvote_sum)
#print(SVMdata.SVMvote_count)
#print(SVMdata.SVMvote_mean)
#print(SVMdata.SVMvote_decision)
##Run parameter optimiser.
params=CreateInitialParams(range=initialParamRange)
print("initial params: ",params)

SVMparams=NestedParamsOptimisation(params,SVMdata,trainingIDgroups,initialParamRange,nestedIterations=nestedIterations,refineRangeFactor=2)
print("Optimised C param: ",SVMparams)
##############################################################
##Run classifier using optimised parameters.
print("Training Classifier with optimised parameters...")
RunClassifiers(SVMdata,trainingIDgroups,SVMparams)
#print(SVMdata.SVMvote_sum)
#print(SVMdata.SVMvote_count)
#print(SVMdata.SVMvote_mean)
#print(SVMdata.SVMvote_decision)
print("\nClassifier ready for use.")

##Adjust threshold for recall.
#AdjustThresholdForRecall(SVMdata,startingThreshold,minRecall)

##Adjust threshold for kappa.
AdjustThresholdForKappa(SVMdata,startingThreshold)

##Make review recommendations based on analysis and threshold.
numReturn=SVM_recommendReview(SVMdata)
##Make random review recommendations.
SVM_recommendReview_random(SVMdata,numReturn)
##Export the recommendations and the key file.
exportRecommendations(SVMdata)


#############################################
#Print the size of the vocab.
print("vocabSize: ",len(SVMdata.Feature_names))

#####################################################
##Report on program runtime.
print("Program took",int(time.time()-startTime),"seconds to run.")

##Prompt to exit program.
input('Press ENTER to exit')
