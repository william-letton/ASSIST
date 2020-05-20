import time
import csv
import math
from Screening.models import Article,Project
from Screening.ScreeningCeleryTasks import ReconcileTidyAsynch

## Define a character list of the punctuations to be removed during processing.
punctuations = "•™©!£$€/\%^&*+±=()â‰¥[]|0123456789'=.,:;?%<>ÿòñ~#@-—–{}úøîæ÷ó¬åà®¯§"+'"“”'

def SuggestTagsMain(project,request):

    ## Note start time for testing.
    start = time.time()
    print("start: ",time.time())

    #Get the correct abstracts - Pooled tags or individual or gold standard choice
    abstracts,screening_codes= GetDataForSuggester(project,request)

    #Get count
    count_all_abstracts=len(abstracts)
    print("number of abstracts: ",count_all_abstracts)

    #Make abstracts lower
    all_abstracts_lower = GetAbstractsInLower(abstracts)

    ## Create a list of screening codes without repetition.
    screening_codes_key = list()
    for code in project.allowedTags.all():
        screening_codes_key.append(code.Tag)

    ## Split abstracts into words and put into vocabulary list.
    vocabulary = GetOurVocabulary(all_abstracts_lower,count_all_abstracts)
    vocabulary_length=len(vocabulary)
    print("length of vocabulary: ", vocabulary_length)

    ## Calculating TF values.Create a dictionary to store the total number of words for each screening code.
    print("start calculating TF values: ",time.time())
    SCabstractsWordsNum, TFdict = GetTFDictSCabsts(all_abstracts_lower, count_all_abstracts, screening_codes_key, vocabulary,screening_codes)

    ## For each word in each screening code, divide the number of occurances by the total number of words for that screening code.
    TFdict = GetTFDictFinal(TFdict,SCabstractsWordsNum)

    ## Calculate IDF values.
    print("start calculating IDF values: ",time.time())
    IDFdict = Pop0IDFDict(vocabulary)

    #Log scale IDFDict
    IDFdict = LogScaleIDFdict(IDFdict, all_abstracts_lower, count_all_abstracts, vocabulary)

    ## Calculate TF-IDF values.
    print("start calculating TF-IDF values: ",time.time())

    ## Create a dictionary to store the results.
    TFIDFdict = GetTFIDFdict(IDFdict, TFdict, screening_codes_key, vocabulary)

    ## Print keyWord
    for code in TFIDFdict:
        l=list()
        for key,val in TFIDFdict[code].items():
            l.append((val,key))
        l.sort(reverse=True)
        print("\n",code)
        for key,value in l[0:15]:
            print(value)

    print("End: ",time.time())
    print("Program took",time.time()-start,"seconds to run.")

#returns our abstracts in a list (Full article object)
def GetDataForSuggester(project,request):
    starsugg = time.time()
    AbstractsList = list()
    screening_codes = list()
    Type = request.POST["PoolType"]
    
    #Gold standard - Only reconciled
    if Type == "GoldStan":
        ReconcileTidyAsynch(project.UniqueID,False)
        goldsubset = project.assignedarticles.exclude(finalResult = None)
        for article in goldsubset.all():
            #Get our content
            AbstractsList.append(article.content)
            #Get our tag
            screening_codes.append(article.finalResult.screeningTag.Tag)
    
            #All abstracts and screening codes
    if Type == "AllTag":
        allsubset = project.assignedarticles.exclude(screeningResults = None)
        for article in allsubset.all():
            priortags = list()
            for tag in article.screeningResults.all():
                #No point in adding multiple times
                if tag.screeningTag.Tag in priortags:
                    continue
                AbstractsList.append(article.content)
                screening_codes.append(tag.screeningTag.Tag)
                priortags.append(tag.screeningTag.Tag)

    #User's codes
    if Type == "MyTag":
        userssubset = project.assignedarticles.filter(screeningResults__personScreening__pk = request.user.pk)
        for article in userssubset.all():
            #Get our content
            AbstractsList.append(article.content)
            #Get our tags
            for code in article.screeningResults.all():
                if code.personScreening == request.user:
                    screening_codes.append(code.screeningTag.Tag)
    print("Getting Data took : " , time.time()-starsugg)
    #return what we have found
    return AbstractsList,screening_codes


def GetAbstractsInLower(abstracts):
    ## Process the list of abstracts to remove punctuation and make lowercase
    all_abstracts_nopunct=[]

    #Add all of our characters bar punctuatuion
    for abstract in abstracts:
        no_punct=""
        for character in abstract:
            if character not in punctuations:
                no_punct= no_punct+character
        all_abstracts_nopunct.append(no_punct)
    #print("abstracts after no punctutation: ",all_abstracts_nopunct)

    #Get to lowercase
    all_abstracts_lower=[]
    for abstract in all_abstracts_nopunct:
        all_abstracts_lower.append(abstract.lower())
    #print("abstracts after lowercase: ",all_abstracts_lower)
    #Return our result
    return all_abstracts_lower

def GetOurVocabulary(all_abstracts_lower,count_all_abstracts):
    vocabulary=dict()
    for abstract in all_abstracts_lower:
        split=abstract.split()
        for word in split:
            vocabulary[word]=vocabulary.get(word,0)+1
    #print("vocabulary: ",vocabulary)
    print("vocabulary length before processing: ",len(vocabulary))
    # Take rare words out of vocabulary (to decrease run time later on).
    exWords=list()
    lowThreshold=1+((count_all_abstracts/200)**1.5)
    print("word count threshold for vocabulary inclusion: ",lowThreshold)
    for word in vocabulary:
        if vocabulary[word]<lowThreshold:
            exWords.append(str(word))
    for word in exWords:
        del vocabulary[word]
    print("vocabulary length after processing: ",len(vocabulary))
    vocabulary=list(set(vocabulary))
    return vocabulary

def GetTFDictSCabsts(all_abstracts_lower, count_all_abstracts, screening_codes_key, vocabulary,screening_codes):
    SCabstractsWordsNum=dict()
    ## Create a dictionary to store the TF values.
    TFdict=dict()
    for code in screening_codes_key:
        TFdict[code]={}
        SCabstractsWordsNum[code]=0
    
    
    ## Insert all the words from the vocabulary into each screening code
    ## subdictionary, so that all subdictionaries have the same number of entries
    for i in TFdict:
        for j in vocabulary:
            TFdict[i][j]=0
    
    ## Create a concatenated string of all of the abstracts of that screening code.
    for i in TFdict:
        ## Create an empty vector for boolean values
        bool=[]
        ## Create an empty list for abstracts text
        abstracts_text=[]
        # Compare the code to the screening_codes list to produce a list of true/false
        for j in screening_codes:
            if i==j:
                #print("True")
                bool.append(True)
            else:
                #print("False")
                bool.append(False)
        for l in range(0,count_all_abstracts):
            #print(l)
            if bool[l]==True:
                split=all_abstracts_lower[l].split()
                for word in split:
                    if word in vocabulary:
                        TFdict[i][word]=TFdict[i][word]+1
                        SCabstractsWordsNum[i]=SCabstractsWordsNum[i]+1
    #print("TFdict after counting words in abstracts: ",TFdict)
    #print("SCabstractsWordsNum after counting words in abstracts: ",SCabstractsWordsNum)
    return SCabstractsWordsNum, TFdict

def Pop0IDFDict(vocabulary):
    IDFdict=dict()
    for word in vocabulary:
        IDFdict[word]=0
    print("done setting 0 values: ",time.time())
    #print("IDFdict before population: ",IDFdict)
    return IDFdict

def GetTFDictFinal(TFdict,SCabstractsWordsNum):
    for code in TFdict:
        for word in TFdict[code]:
            TFdict[code][word]=TFdict[code][word]/SCabstractsWordsNum[code]
    #print("TFdict final: ",TFdict)
    return TFdict

def LogScaleIDFdict(IDFdict, all_abstracts_lower, count_all_abstracts, vocabulary):
    for word in vocabulary:
        for abstract in all_abstracts_lower:
            split=abstract.split()
            if word in split:
                IDFdict[word]=IDFdict[word]+1
        IDFdict[word]=math.log(count_all_abstracts/IDFdict[word],10)
    #print("IDFdict after log-scaled inverse : ",IDFdict)
    return IDFdict

def GetTFIDFdict(IDFdict, TFdict, screening_codes_key, vocabulary):
    TFIDFdict=dict()
    for code in screening_codes_key:
        TFIDFdict[code]={}
    #print("TFIDFdict unpopulated: ",TFIDFdict)
    ##for each screening code for each vocabulary word, multiply TF and IDF into TFIDFdict
    for code in TFIDFdict:
        for word in vocabulary:
            TFIDFdict[code][word]=TFdict[code][word]*IDFdict[word]
    #print("TFIDFdict populated: ",TFIDFdict)
    print("start sorting keyword by value and printing: ",time.time())
    return TFIDFdict