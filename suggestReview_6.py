##This version will not detect or remove duplicates

import time
startTime = time.time()
import math
import csv
from random import seed
from random import randint
##define the punctuations to be removed
punctuations = "_çìëá•™©!£$€/%^&*+±=()â‰¥[]|0123456789'=.,:;?%<>ÿòñ~#@-—–{}úøîæ÷ó¬åà®¯§"+'"“”'
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
    #contentWordListSet=[]
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
    recommendReview_random=False
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
        #self.contentWordListSet=list(set(l))

        ##create 2-word N-grams from the words list.
        l2=list()
        for pos in range(0,len(self.contentWordList)-1):
            l2.append(self.contentWordList[pos]+" "+self.contentWordList[pos+1])
        self.contentWord2List=l2

    ##Assigning tags
    def NBcodon4(self,nam):
        self.tag_nb_codon4=nam
    def NBword(self,nam):
        self.tag_nb_word=nam
    def suggestTag(self,nam):
        self.tag_suggested=nam
    def INprob(self,num):
        self.prob_IN=num
    def INEXassign(self,nam):
        self.assignment_suggested=nam
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
        inputColGoldAssignment = "D"
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
##create a dictionary of tag-assignment pairs (e.g. "3.IN_METHOD", "IN")
def DefineTagAssignment(articles_train,articles_test):
    ##Define which tags are IN or EX, and check that this is consistent.
    def DefineAssignment(articles):
        ##Create a list of unique tags.
        def extractUniqueTags(articles):
            print("\nExtracting unique screening tags...")
            tagList=[]
            for article in articles:
                tagList.append(article.goldTag)
            tagList=list(set(tagList))
            return(tagList)
        uniqueTags=extractUniqueTags(articles)
        ##Create a dictionary of unique tags as keys and lists of all the assignment
        ## values as values.
        assDict=dict()
        for tag in uniqueTags:
            assDict[tag]=list()
        for article in articles:
            assDict[article.goldTag].append(article.goldAssignment)
        #print(assDict)
        for tag in assDict:
            assDict[tag]=list(set(assDict[tag]))
        #print(assDict)
        ##Check for tags with multiple assignments (i.e. both IN and EX)
        for tag in assDict:
            if len(assDict[tag])>1:
                print("Inconsistent tag assignment.")
                print(tag,"is listed as",assDict[tag])
                print("Please resolve this conflict in input file and try again.")
                input('Press ENTER to exit')
                quit()
        print("All tags are consistently assigned")
        ##simply each list to a string.
        for tag in assDict:
            assDict[tag]=(assDict[tag][0])
        return(assDict)
    train=DefineAssignment(articles_train)
    test=DefineAssignment(articles_test)
    ##compare the tag-assignment pairs between training and testing data
    print("Comparing tag assignments in training and testing datasets...")
    for tag in train:
        try:
            if train[tag]!=test[tag]:
                print("Tag assignments do not match between training and testing datasets.")
                print(tag,train[tag],test[tag])
                print("Resolve these assignments in the input files and try again.")
                input('Press ENTER to exit')
                quit()
        except:
            print("tag ",tag," occurs in the training data, but not in the testing data.")
    print("Training and testing tag assignments agree.")
    print("Tag assignments: ")
    for tag in train:
        print(tag," > ",train[tag])
    return(train)
## Run naive bayes classifiers.
def NB_codon4(trainArticles,testArticles):
    ## Train the algorithm on the imported training data.
    def NBTrain_codon4(articles):
        count_all_abstracts=len(articles)
        print("number of abstracts: ",count_all_abstracts)
        ##Create a list of unique screening tags
        def extractUniqueTags(articles):
            print("Extracting unique screening tags...")
            tagList=[]
            for article in articles:
                tagList.append(article.goldTag)
            tagList=list(set(tagList))
            return(tagList)
        tagsKey=extractUniqueTags(articles)
        print("unique screening tags in training data: ",tagsKey)
        ##create a dictionary of tags and their counts
        def calculateTagPriors(articles,numAbstracts):
            print("Calculating tag prior probabilities...")
            d=dict()
            d2=dict()
            l=list()
            for article in articles:
                l.append(article.goldTag)
            for tag in l:
                d[tag]=d.get(tag,0)+1
            for tag in d:
                d2[tag]=d[tag]/numAbstracts
            return(d2)
        tagPriors=calculateTagPriors(articles,count_all_abstracts)
        ##Create a vocabulary of all unique codons.
        def createVocabulary(articles):
            print("Populating vocabulary...")
            v=dict()
            for article in articles:
                for codon in article.codonFourList:
                    v[codon]=v.get(codon,0)+1
            return(v)
        vocab=createVocabulary(articles)
        ##Create a dictionary containing the prior probabilities for each codon for
        ##each screening tag.
        def calculateCodonCounts(articles,tagsKey,vocab):
            print("Calculating codon prior probabilities...")
            ##create a dictionary with a subdictionary for each tag. Each subdictionary
            ## contains all the words from the vocabulary, with a starting value of 0.
            countByTag=dict()
            for i in tagsKey:
                countByTag[i]={}
            for i in countByTag:
                for j in vocab:
                    countByTag[i][j]=vocab[j]*0
            ##Create a list of all of the screening codes, in the same order as the articles.
            screening_codes=[]
            for article in articles:
                screening_codes.append(article.goldTag)
            ##Compare each screening code to each item in the screening codes list,
            ##creating a boolean vector.
            for i in tagsKey:
                bool=[]
                for j in screening_codes:
                    if i==j:
                        bool.append(True)
                    else:
                        bool.append(False)
                abs_num=sum(bool)
                for l in range(0,len(articles)):
                    if bool[l]==True:
                        for codon in articles[l].codonFourList:
                            countByTag[i][codon]=countByTag[i][codon]+1
            return(countByTag)
        words_count_by_screening_code=calculateCodonCounts(articles,tagsKey,vocab)
        ##Calculate the total number of codon positions for each screening tag.
        def calculateCodonsPerTag(tagsKey,codonCount):
            print("Calculating codons per screening tag...")
            d=dict()
            for i in tagsKey:
                d[i]={}
                d[i]=sum(codonCount[i].values())
            return(d)
        total_words_num_per_screening_code=calculateCodonsPerTag(tagsKey,words_count_by_screening_code)
        ## Calculate the prior probabilities of each codon for each tag separately.
        def calculateCodonPriorsPerTag(vocab,TagsKey,codonCount,codonsPerTag):
            print("Calculating tag prior probabilities...")
            d=dict()
            vocabLength=(len(vocab))
            for i in TagsKey:
                d[i]={}
            for i in d:
                for c in codonCount[i]:
                    d[i][c]=(  (  codonCount[i][c] +1  )    /   (codonsPerTag[i]   +  vocabLength         ) )
            return(d)
        codonPriorsPerTag=calculateCodonPriorsPerTag(vocab,tagsKey,words_count_by_screening_code,total_words_num_per_screening_code)
        print("Training complete.\n")
        collected=list()
        collected.append(tagsKey)
        collected.append(tagPriors)
        collected.append(vocab)
        collected.append(codonPriorsPerTag)
        return(collected)
    ## Calculate the relative probabilities of each tag for each abstract.
    def NBTest_codon4(articles,tagsKey,tagPriors,vocab,codonPriorsPerTag):
        print("Calculating probabilities...")
        ##create dictionary for the results of the probability calculations.
        r=dict()
        for article in articles:
            r[article.ID]={}
        ## First calculate tag probability based on tag priors.
        for id in r:
            for tag in tagsKey:
                r[id][tag]=math.log(tagPriors[tag],10)
        ## Now multiple that tag probability by the priors for each codon.
        countArticles = len(articles)
        currentCount = 0
        percentDone1=0
        percentDone2=0
        for article in articles:
            for codon in article.codonFourList:
                for tag in tagsKey:
                    if codon in vocab:
                        r[article.ID][tag]=(r[article.ID][tag])+math.log(codonPriorsPerTag[tag][codon],10)
                    else:
                        continue
            currentCount=currentCount+1
            percentDone2=((currentCount/countArticles)*100)
            if percentDone2-percentDone1 >5:
                print("    ",int(percentDone2),"%")
                percentDone1=percentDone2
        ## Normalise the probability values so that the values for all the tags for
        ## each abstract sum to 1.
        for abstract in r:
            k=[]
            for c in r[abstract]:
                k.append(r[abstract][c])
            sumk=sum(k)
            for c in r[abstract]:
                r[abstract][c]=1-(r[abstract][c]/sumk)
            s=0
            for c in r[abstract]:
                s=s+r[abstract][c]
            for c in r[abstract]:
                r[abstract][c]=r[abstract][c]/s
        #print(r)
        return(r)
    NBTrained_codon4=NBTrain_codon4(trainArticles)
    NBtagProbs_codon4=NBTest_codon4(testArticles,NBTrained_codon4[0],NBTrained_codon4[1],NBTrained_codon4[2],NBTrained_codon4[3])
    return(NBtagProbs_codon4)
def NB_codon3(trainArticles,testArticles):
    ## Train the algorithm on the imported training data.
    def NBTrain_codon4(articles):
        count_all_abstracts=len(articles)
        print("number of abstracts: ",count_all_abstracts)
        ##Create a list of unique screening tags
        def extractUniqueTags(articles):
            print("Extracting unique screening tags...")
            tagList=[]
            for article in articles:
                tagList.append(article.goldTag)
            tagList=list(set(tagList))
            return(tagList)
        tagsKey=extractUniqueTags(articles)
        print("unique screening tags in training data: ",tagsKey)
        ##create a dictionary of tags and their counts
        def calculateTagPriors(articles,numAbstracts):
            print("Calculating tag prior probabilities...")
            d=dict()
            d2=dict()
            l=list()
            for article in articles:
                l.append(article.goldTag)
            for tag in l:
                d[tag]=d.get(tag,0)+1
            for tag in d:
                d2[tag]=d[tag]/numAbstracts
            return(d2)
        tagPriors=calculateTagPriors(articles,count_all_abstracts)
        ##Create a vocabulary of all unique codons.
        def createVocabulary(articles):
            print("Populating vocabulary...")
            v=dict()
            for article in articles:
                for codon in article.codonThreeList:
                    v[codon]=v.get(codon,0)+1
            return(v)
        vocab=createVocabulary(articles)
        ##Create a dictionary containing the prior probabilities for each codon for
        ##each screening tag.
        def calculateCodonCounts(articles,tagsKey,vocab):
            print("Calculating codon prior probabilities...")
            ##create a dictionary with a subdictionary for each tag. Each subdictionary
            ## contains all the words from the vocabulary, with a starting value of 0.
            countByTag=dict()
            for i in tagsKey:
                countByTag[i]={}
            for i in countByTag:
                for j in vocab:
                    countByTag[i][j]=vocab[j]*0
            ##Create a list of all of the screening codes, in the same order as the articles.
            screening_codes=[]
            for article in articles:
                screening_codes.append(article.goldTag)
            ##Compare each screening code to each item in the screening codes list,
            ##creating a boolean vector.
            for i in tagsKey:
                bool=[]
                for j in screening_codes:
                    if i==j:
                        bool.append(True)
                    else:
                        bool.append(False)
                abs_num=sum(bool)
                for l in range(0,len(articles)):
                    if bool[l]==True:
                        for codon in articles[l].codonThreeList:
                            countByTag[i][codon]=countByTag[i][codon]+1
            return(countByTag)
        words_count_by_screening_code=calculateCodonCounts(articles,tagsKey,vocab)
        ##Calculate the total number of codon positions for each screening tag.
        def calculateCodonsPerTag(tagsKey,codonCount):
            print("Calculating codons per screening tag...")
            d=dict()
            for i in tagsKey:
                d[i]={}
                d[i]=sum(codonCount[i].values())
            return(d)
        total_words_num_per_screening_code=calculateCodonsPerTag(tagsKey,words_count_by_screening_code)
        ## Calculate the prior probabilities of each codon for each tag separately.
        def calculateCodonPriorsPerTag(vocab,TagsKey,codonCount,codonsPerTag):
            print("Calculating tag prior probabilities...")
            d=dict()
            vocabLength=(len(vocab))
            for i in TagsKey:
                d[i]={}
            for i in d:
                for c in codonCount[i]:
                    d[i][c]=(  (  codonCount[i][c] +1  )    /   (codonsPerTag[i]   +  vocabLength         ) )
            return(d)
        codonPriorsPerTag=calculateCodonPriorsPerTag(vocab,tagsKey,words_count_by_screening_code,total_words_num_per_screening_code)
        print("Training complete.\n")
        collected=list()
        collected.append(tagsKey)
        collected.append(tagPriors)
        collected.append(vocab)
        collected.append(codonPriorsPerTag)
        return(collected)
    ## Calculate the relative probabilities of each tag for each abstract.
    def NBTest_codon4(articles,tagsKey,tagPriors,vocab,codonPriorsPerTag):
        print("Calculating probabilities...")
        ##create dictionary for the results of the probability calculations.
        r=dict()
        for article in articles:
            r[article.ID]={}
        ## First calculate tag probability based on tag priors.
        for id in r:
            for tag in tagsKey:
                r[id][tag]=math.log(tagPriors[tag],10)
        ## Now multiple that tag probability by the priors for each codon.
        countArticles = len(articles)
        currentCount = 0
        percentDone1=0
        percentDone2=0
        for article in articles:
            for codon in article.codonThreeList:
                for tag in tagsKey:
                    if codon in vocab:
                        r[article.ID][tag]=(r[article.ID][tag])+math.log(codonPriorsPerTag[tag][codon],10)
                    else:
                        continue
            currentCount=currentCount+1
            percentDone2=((currentCount/countArticles)*100)
            if percentDone2-percentDone1 >5:
                print("    ",int(percentDone2),"%")
                percentDone1=percentDone2
        ## Normalise the probability values so that the values for all the tags for
        ## each abstract sum to 1.
        for abstract in r:
            k=[]
            for c in r[abstract]:
                k.append(r[abstract][c])
            sumk=sum(k)
            for c in r[abstract]:
                r[abstract][c]=1-(r[abstract][c]/sumk)
            s=0
            for c in r[abstract]:
                s=s+r[abstract][c]
            for c in r[abstract]:
                r[abstract][c]=r[abstract][c]/s
        #print(r)
        return(r)
    NBTrained_codon4=NBTrain_codon4(trainArticles)
    NBtagProbs_codon4=NBTest_codon4(testArticles,NBTrained_codon4[0],NBTrained_codon4[1],NBTrained_codon4[2],NBTrained_codon4[3])
    return(NBtagProbs_codon4)
def NB_word(trainArticles,testArticles):
    ## Train the algorithm on the imported training data.
    def NBTrain_word(articles):
        count_all_abstracts=len(articles)
        print("number of abstracts: ",count_all_abstracts)
        ##Create a list of unique screening tags
        def extractUniqueTags(articles):
            print("Extracting unique screening tags...")
            tagList=[]
            for article in articles:
                tagList.append(article.goldTag)
            tagList=list(set(tagList))
            return(tagList)
        tagsKey=extractUniqueTags(articles)
        print("unique screening tags in training data: ",tagsKey)
        ##create a dictionary of tags and their counts
        def calculateTagPriors(articles,numAbstracts):
            print("Calculating tag prior probabilities...")
            d=dict()
            d2=dict()
            l=list()
            for article in articles:
                l.append(article.goldTag)
            for tag in l:
                d[tag]=d.get(tag,0)+1
            for tag in d:
                d2[tag]=d[tag]/numAbstracts
            return(d2)
        tagPriors=calculateTagPriors(articles,count_all_abstracts)
        ##Create a vocabulary of all unique codons.
        def createVocabulary(articles):
            print("Populating vocabulary...")
            v=dict()
            for article in articles:
                for codon in article.contentWordList:
                    v[codon]=v.get(codon,0)+1
            return(v)
        vocab=createVocabulary(articles)
        ##Create a dictionary containing the prior probabilities for each codon for
        ##each screening tag.
        def calculateCodonCounts(articles,tagsKey,vocab):
            print("Calculating codon prior probabilities...")
            ##create a dictionary with a subdictionary for each tag. Each subdictionary
            ## contains all the words from the vocabulary, with a starting value of 0.
            countByTag=dict()
            for i in tagsKey:
                countByTag[i]={}
            for i in countByTag:
                for j in vocab:
                    countByTag[i][j]=vocab[j]*0
            ##Create a list of all of the screening codes, in the same order as the articles.
            screening_codes=[]
            for article in articles:
                screening_codes.append(article.goldTag)
            ##Compare each screening code to each item in the screening codes list,
            ##creating a boolean vector.
            for i in tagsKey:
                bool=[]
                for j in screening_codes:
                    if i==j:
                        bool.append(True)
                    else:
                        bool.append(False)
                abs_num=sum(bool)
                for l in range(0,len(articles)):
                    if bool[l]==True:
                        for codon in articles[l].contentWordList:
                            countByTag[i][codon]=countByTag[i][codon]+1
            return(countByTag)
        words_count_by_screening_code=calculateCodonCounts(articles,tagsKey,vocab)
        ##Calculate the total number of codon positions for each screening tag.
        def calculateCodonsPerTag(tagsKey,codonCount):
            print("Calculating codons per screening tag...")
            d=dict()
            for i in tagsKey:
                d[i]={}
                d[i]=sum(codonCount[i].values())
            return(d)
        total_words_num_per_screening_code=calculateCodonsPerTag(tagsKey,words_count_by_screening_code)
        ## Calculate the prior probabilities of each codon for each tag separately.
        def calculateCodonPriorsPerTag(vocab,TagsKey,codonCount,codonsPerTag):
            print("Calculating tag prior probabilities...")
            d=dict()
            vocabLength=(len(vocab))
            for i in TagsKey:
                d[i]={}
            for i in d:
                for c in codonCount[i]:
                    d[i][c]=(  (  codonCount[i][c] +1  )    /   (codonsPerTag[i]   +  vocabLength         ) )
            return(d)
        codonPriorsPerTag=calculateCodonPriorsPerTag(vocab,tagsKey,words_count_by_screening_code,total_words_num_per_screening_code)
        print("Training complete.\n")
        collected=list()
        collected.append(tagsKey)
        collected.append(tagPriors)
        collected.append(vocab)
        collected.append(codonPriorsPerTag)
        return(collected)
    ## Calculate the relative probabilities of each tag for each abstract.
    def NBTest_word(articles,tagsKey,tagPriors,vocab,codonPriorsPerTag):
        print("Calculating probabilities...")
        ##create dictionary for the results of the probability calculations.
        r=dict()
        for article in articles:
            r[article.ID]={}
        ## First calculate tag probability based on tag priors.
        for id in r:
            for tag in tagsKey:
                r[id][tag]=math.log(tagPriors[tag],10)
        ## Now multiple that tag probability by the priors for each codon.
        countArticles = len(articles)
        currentCount = 0
        percentDone1=0
        percentDone2=0
        for article in articles:
            for codon in article.contentWordList:
                for tag in tagsKey:
                    if codon in vocab:
                        r[article.ID][tag]=(r[article.ID][tag])+math.log(codonPriorsPerTag[tag][codon],10)
                    else:
                        continue
            currentCount=currentCount+1
            percentDone2=((currentCount/countArticles)*100)
            if percentDone2-percentDone1 >5:
                print("    ",int(percentDone2),"%")
                percentDone1=percentDone2
        ## Normalise the probability values so that the values for all the tags for
        ## each abstract sum to 1.
        for abstract in r:
            k=[]
            for c in r[abstract]:
                k.append(r[abstract][c])
            sumk=sum(k)
            for c in r[abstract]:
                r[abstract][c]=1-(r[abstract][c]/sumk)
            s=0
            for c in r[abstract]:
                s=s+r[abstract][c]
            for c in r[abstract]:
                r[abstract][c]=r[abstract][c]/s
        return(r)
    NBTrained_word=NBTrain_word(trainArticles)
    NBtagProbs_word=NBTest_word(testArticles,NBTrained_word[0],NBTrained_word[1],NBTrained_word[2],NBTrained_word[3])
    return(NBtagProbs_word)
#def NB_word_TFIDF(trainArticles,testArticles):
    ## Train the algorithm on the imported training data.
    def NBTrain_codon4(articles):
        count_all_abstracts=len(articles)
        print("number of abstracts: ",count_all_abstracts)
        ##Create a list of unique screening tags
        def extractUniqueTags(articles):
            print("Extracting unique screening tags...")
            tagList=[]
            for article in articles:
                tagList.append(article.goldTag)
            tagList=list(set(tagList))
            return(tagList)
        tagsKey=extractUniqueTags(articles)
        print("unique screening tags in training data: ",tagsKey)
        ##create a dictionary of tags and their counts
        def calculateTagPriors(articles,numAbstracts):
            print("Calculating tag prior probabilities...")
            d=dict()
            d2=dict()
            l=list()
            for article in articles:
                l.append(article.goldTag)
            for tag in l:
                d[tag]=d.get(tag,0)+1
            for tag in d:
                d2[tag]=d[tag]/numAbstracts
            ##returning the tag prior as a log so that it can be added to the codon
            ##prior log in the testing stage.
            print("TFIDF tag priors: ",d2)
            return(d2)
        tagPriors=calculateTagPriors(articles,count_all_abstracts)
        ##Create a vocabulary of all unique codons, counted for each inistance they appear.
        def createVocabulary(articles):
            print("Populating vocabulary...")
            v=dict()
            for article in articles:
                for codon in article.contentWordList:
                    v[codon]=v.get(codon,0)+1
            return(v)
        vocab=createVocabulary(articles)

        ##Create a vocabulary of all unique codons, counted for each article in which they appear.
        def createVocabularySet(articles):
            print("Populating vocabulary...")
            v=dict()
            for article in articles:
                for codon in article.contentWordListSet:
                    v[codon]=v.get(codon,0)+1
            return(v)
        vocabSet=createVocabularySet(articles)


        ##Create a dictionary containing the prior probabilities for each codon for
        ##each screening tag.
        def calculateCodonCounts(articles,tagsKey,vocab):
            print("Calculating codon prior probabilities...")
            ##create a dictionary with a subdictionary for each tag. Each subdictionary
            ## contains all the words from the vocabulary, with a starting value of 0.
            countByTag=dict()
            for tag in tagsKey:
                countByTag[tag]={}
            for tag in countByTag:
                for codon in vocab:
                    ##each codon for each tag is given a starting count of 1. This
                    ##prevents TF from being 0 and so TFIDF from being 0.
                    countByTag[tag][codon]=1
            for tag in countByTag:
                for article in articles:
                    if article.goldTag==tag:
                        for codon in article.contentWordList:
                            countByTag[tag][codon]=countByTag[tag][codon]+1
            return(countByTag)
        words_count_by_screening_code=calculateCodonCounts(articles,tagsKey,vocab)
        ##Calculate the total number of codon positions for each screening tag.
        def calculateCodonsPerTag(tagsKey,codonCount):
            print("Calculating codons per screening tag...")
            d=dict()
            for i in tagsKey:
                d[i]={}
                d[i]=sum(codonCount[i].values())
            return(d)
        total_words_num_per_screening_code=calculateCodonsPerTag(tagsKey,words_count_by_screening_code)

        ##for the IDF calculation we need to know the proprtion off all articles
        ##that the codon appears in. For this we use the vocabSet dictionary.
        def calculateCodonPrevalence(vocabSet,articles):
            print("Calculating codon prevalances...")
            d=dict()
            for codon in vocabSet:
                ##Calculate the prevalence of the codon. Adding 1 to the length
                ##of the articles prevents the prevalence from reaching 1 and therefore
                ##stops log(1/prevalance) from becoming 0 and therefore IDF from
                ##becoming 0.
                d[codon]=vocabSet[codon]/(len(articles)+1)
            return(d)
        codonPrevalenceDict=calculateCodonPrevalence(vocabSet,articles)
        #print("codonPrevalenceDict: ",codonPrevalenceDict)
        #templist=list()
        #for key,val in codonPrevalenceDict.items():
        #    templist.append((val,key))
        #templist.sort()
        #print(templist)

        ## Calculate the prior probabilities of each codon for each tag separately.
        def calculateTFIDF(codonPrevalenceDict,tagsKey,codonCount,codonsPerTag,articles):
            tf=dict()
            for tag in tagsKey:
                tf[tag]={}
            for tag in tf:
                for codon in codonPrevalenceDict:
                    #print("TEST: ",len(articles),vocab[codon])
                    tf[tag][codon]=(codonCount[tag][codon]/codonsPerTag[tag])*math.log((1/codonPrevalenceDict[codon]),10)
                    #if tf[tag][codon]<0:
                    #    print(codon)
            return(tf)
        codonPriors=calculateTFIDF(codonPrevalenceDict,tagsKey,words_count_by_screening_code,total_words_num_per_screening_code,articles)
        #def calculateCodonPriorsPerTag(vocab,TagsKey,codonCount,codonsPerTag):
        #    print("Calculating tag prior probabilities...")
        #    d=dict()
        #    vocabLength=(len(vocab))
        #    for i in TagsKey:
        #        d[i]={}
        #    for i in d:
        #        for c in codonCount[i]:
        #            d[i][c]=(  (  codonCount[i][c] +1  )    /   (codonsPerTag[i]   +  vocabLength         ) )

        #codonPriorsPerTag=calculateCodonPriorsPerTag(vocab,tagsKey,words_count_by_screening_code,total_words_num_per_screening_code)
        print("Training complete.\n")
        collected=list()
        collected.append(tagsKey)
        collected.append(tagPriors)
        collected.append(vocab)
        collected.append(codonPriors)
        #print("Codon Priors: ", codonPriors)
        return(collected)
    ## Calculate the relative probabilities of each tag for each abstract.
    def NBTest_codon4(articles,tagsKey,tagPriors,vocab,codonPriorsPerTag):
        print("Calculating probabilities...")
        #print(tagPriors)
        ##create dictionary for the results of the probability calculations.
        r=dict()
        for article in articles:
            r[article.ID]={}
        ## First calculate tag probability based on tag priors.
        for id in r:
            for tag in tagsKey:
                r[id][tag]=tagPriors[tag]
        #print(r)
                #print("ght: ",r[id][tag])
        ## Now multiple that tag probability by the priors for each codon.
        countArticles = len(articles)
        currentCount = 0
        percentDone1=0
        percentDone2=0
        for article in articles:
            for codon in article.contentWordList:
                for tag in tagsKey:
                    if codon in vocab:
                        #print("shagh: ",r[article.ID][tag],codonPriorsPerTag[tag][codon])
                        #r[article.ID][tag]=(r[article.ID][tag])+math.log(codonPriorsPerTag[tag][codon],10)
                        r[article.ID][tag]=r[article.ID][tag]*codonPriorsPerTag[tag][codon]
                    else:
                        continue
                #print(r)
                ##renormalise the probability values after each codon calculation.
                currentProbs=list()
                for tag in r[article.ID]:
                    currentProbs.append(r[article.ID][tag])
                currentSum=sum(currentProbs)
                for tag in r[article.ID]:
                    r[article.ID][tag]=r[article.ID][tag]/currentSum
            #print(r)
            ##keep track of progress
            currentCount=currentCount+1
            percentDone2=((currentCount/countArticles)*100)
            if percentDone2-percentDone1 >5:
                print("    ",int(percentDone2),"%")
                percentDone1=percentDone2
        print(r)
        return(r)
    NBTrained_codon4=NBTrain_codon4(trainArticles)
    NBtagProbs_codon4=NBTest_codon4(testArticles,NBTrained_codon4[0],NBTrained_codon4[1],NBTrained_codon4[2],NBTrained_codon4[3])
    return(NBtagProbs_codon4)
def NB_word2(trainArticles,testArticles):
    ## Train the algorithm on the imported training data.
    def NBTrain_word(articles):
        count_all_abstracts=len(articles)
        print("number of abstracts: ",count_all_abstracts)
        ##Create a list of unique screening tags
        def extractUniqueTags(articles):
            print("Extracting unique screening tags...")
            tagList=[]
            for article in articles:
                tagList.append(article.goldTag)
            tagList=list(set(tagList))
            return(tagList)
        tagsKey=extractUniqueTags(articles)
        print("unique screening tags in training data: ",tagsKey)
        ##create a dictionary of tags and their counts
        def calculateTagPriors(articles,numAbstracts):
            print("Calculating tag prior probabilities...")
            d=dict()
            d2=dict()
            l=list()
            for article in articles:
                l.append(article.goldTag)
            for tag in l:
                d[tag]=d.get(tag,0)+1
            for tag in d:
                d2[tag]=d[tag]/numAbstracts
            return(d2)
        tagPriors=calculateTagPriors(articles,count_all_abstracts)
        ##Create a vocabulary of all unique codons.
        def createVocabulary(articles):
            print("Populating vocabulary...")
            v=dict()
            for article in articles:
                for codon in article.contentWord2List:
                    v[codon]=v.get(codon,0)+1
            return(v)
        vocab=createVocabulary(articles)
        ##Create a dictionary containing the prior probabilities for each codon for
        ##each screening tag.
        def calculateCodonCounts(articles,tagsKey,vocab):
            print("Calculating codon prior probabilities...")
            ##create a dictionary with a subdictionary for each tag. Each subdictionary
            ## contains all the words from the vocabulary, with a starting value of 0.
            countByTag=dict()
            for i in tagsKey:
                countByTag[i]={}
            for i in countByTag:
                for j in vocab:
                    countByTag[i][j]=vocab[j]*0
            ##Create a list of all of the screening codes, in the same order as the articles.
            screening_codes=[]
            for article in articles:
                screening_codes.append(article.goldTag)
            ##Compare each screening code to each item in the screening codes list,
            ##creating a boolean vector.
            for i in tagsKey:
                bool=[]
                for j in screening_codes:
                    if i==j:
                        bool.append(True)
                    else:
                        bool.append(False)
                abs_num=sum(bool)
                for l in range(0,len(articles)):
                    if bool[l]==True:
                        for codon in articles[l].contentWord2List:
                            countByTag[i][codon]=countByTag[i][codon]+1
            return(countByTag)
        words_count_by_screening_code=calculateCodonCounts(articles,tagsKey,vocab)
        ##Calculate the total number of codon positions for each screening tag.
        def calculateCodonsPerTag(tagsKey,codonCount):
            print("Calculating codons per screening tag...")
            d=dict()
            for i in tagsKey:
                d[i]={}
                d[i]=sum(codonCount[i].values())
            return(d)
        total_words_num_per_screening_code=calculateCodonsPerTag(tagsKey,words_count_by_screening_code)
        ## Calculate the prior probabilities of each codon for each tag separately.
        def calculateCodonPriorsPerTag(vocab,TagsKey,codonCount,codonsPerTag):
            print("Calculating tag prior probabilities...")
            d=dict()
            vocabLength=(len(vocab))
            for i in TagsKey:
                d[i]={}
            for i in d:
                for c in codonCount[i]:
                    d[i][c]=(  (  codonCount[i][c] +1  )    /   (codonsPerTag[i]   +  vocabLength         ) )
            return(d)
        codonPriorsPerTag=calculateCodonPriorsPerTag(vocab,tagsKey,words_count_by_screening_code,total_words_num_per_screening_code)
        print("Training complete.\n")
        collected=list()
        collected.append(tagsKey)
        collected.append(tagPriors)
        collected.append(vocab)
        collected.append(codonPriorsPerTag)
        return(collected)
    ## Calculate the relative probabilities of each tag for each abstract.
    def NBTest_word(articles,tagsKey,tagPriors,vocab,codonPriorsPerTag):
        print("Calculating probabilities...")
        ##create dictionary for the results of the probability calculations.
        r=dict()
        for article in articles:
            r[article.ID]={}
        ## First calculate tag probability based on tag priors.
        for id in r:
            for tag in tagsKey:
                r[id][tag]=math.log(tagPriors[tag],10)
        ## Now multiple that tag probability by the priors for each codon.
        countArticles = len(articles)
        currentCount = 0
        percentDone1=0
        percentDone2=0
        for article in articles:
            for codon in article.contentWord2List:
                for tag in tagsKey:
                    if codon in vocab:
                        r[article.ID][tag]=(r[article.ID][tag])+math.log(codonPriorsPerTag[tag][codon],10)
                    else:
                        continue
            currentCount=currentCount+1
            percentDone2=((currentCount/countArticles)*100)
            if percentDone2-percentDone1 >5:
                print("    ",int(percentDone2),"%")
                percentDone1=percentDone2
        ## Normalise the probability values so that the values for all the tags for
        ## each abstract sum to 1.
        for abstract in r:
            k=[]
            for c in r[abstract]:
                k.append(r[abstract][c])
            sumk=sum(k)
            for c in r[abstract]:
                r[abstract][c]=1-(r[abstract][c]/sumk)
            s=0
            for c in r[abstract]:
                s=s+r[abstract][c]
            for c in r[abstract]:
                r[abstract][c]=r[abstract][c]/s
        return(r)
    NBTrained_word=NBTrain_word(trainArticles)
    NBtagProbs_word=NBTest_word(testArticles,NBTrained_word[0],NBTrained_word[1],NBTrained_word[2],NBTrained_word[3])
    return(NBtagProbs_word)
#def NB_codon4_TFIDF(trainArticles,testArticles):
    ## Train the algorithm on the imported training data.
    def NBTrain_codon4(articles):
        count_all_abstracts=len(articles)
        print("number of abstracts: ",count_all_abstracts)
        ##Create a list of unique screening tags
        def extractUniqueTags(articles):
            print("Extracting unique screening tags...")
            tagList=[]
            for article in articles:
                tagList.append(article.goldTag)
            tagList=list(set(tagList))
            return(tagList)
        tagsKey=extractUniqueTags(articles)
        print("unique screening tags in training data: ",tagsKey)
        ##create a dictionary of tags and their counts
        def calculateTagPriors(articles,numAbstracts):
            print("Calculating tag prior probabilities...")
            d=dict()
            d2=dict()
            l=list()
            for article in articles:
                l.append(article.goldTag)
            for tag in l:
                d[tag]=d.get(tag,0)+1
            for tag in d:
                d2[tag]=d[tag]/numAbstracts
            ##returning the tag prior as a log so that it can be added to the codon
            ##prior log in the testing stage.
            print("TFIDF tag priors: ",d2)
            return(d2)
        tagPriors=calculateTagPriors(articles,count_all_abstracts)
        ##Create a vocabulary of all unique codons, counted for each inistance they appear.
        def createVocabulary(articles):
            print("Populating vocabulary...")
            v=dict()
            for article in articles:
                for codon in article.codonFourList:
                    v[codon]=v.get(codon,0)+1
            return(v)
        vocab=createVocabulary(articles)

        ##Create a vocabulary of all unique codons, counted for each article in which they appear.
        def createVocabularySet(articles):
            print("Populating vocabulary...")
            v=dict()
            for article in articles:
                for codon in article.codonFourListSet:
                    v[codon]=v.get(codon,0)+1
            return(v)
        vocabSet=createVocabularySet(articles)


        ##Create a dictionary containing the prior probabilities for each codon for
        ##each screening tag.
        def calculateCodonCounts(articles,tagsKey,vocab):
            print("Calculating codon prior probabilities...")
            ##create a dictionary with a subdictionary for each tag. Each subdictionary
            ## contains all the words from the vocabulary, with a starting value of 0.
            countByTag=dict()
            for tag in tagsKey:
                countByTag[tag]={}
            for tag in countByTag:
                for codon in vocab:
                    ##each codon for each tag is given a starting count of 1. This
                    ##prevents TF from being 0 and so TFIDF from being 0.
                    countByTag[tag][codon]=1
            for tag in countByTag:
                for article in articles:
                    if article.goldTag==tag:
                        for codon in article.codonFourList:
                            countByTag[tag][codon]=countByTag[tag][codon]+1
            return(countByTag)
        words_count_by_screening_code=calculateCodonCounts(articles,tagsKey,vocab)
        ##Calculate the total number of codon positions for each screening tag.
        def calculateCodonsPerTag(tagsKey,codonCount):
            print("Calculating codons per screening tag...")
            d=dict()
            for i in tagsKey:
                d[i]={}
                d[i]=sum(codonCount[i].values())
            return(d)
        total_words_num_per_screening_code=calculateCodonsPerTag(tagsKey,words_count_by_screening_code)

        ##for the IDF calculation we need to know the proprtion off all articles
        ##that the codon appears in. For this we use the vocabSet dictionary.
        def calculateCodonPrevalence(vocabSet,articles):
            print("Calculating codon prevalances...")
            d=dict()
            for codon in vocabSet:
                ##Calculate the prevalence of the codon. Adding 1 to the length
                ##of the articles prevents the prevalence from reaching 1 and therefore
                ##stops log(1/prevalance) from becoming 0 and therefore IDF from
                ##becoming 0.
                d[codon]=vocabSet[codon]/(len(articles)+1)
            return(d)
        codonPrevalenceDict=calculateCodonPrevalence(vocabSet,articles)
        #print("codonPrevalenceDict: ",codonPrevalenceDict)
        #templist=list()
        #for key,val in codonPrevalenceDict.items():
        #    templist.append((val,key))
        #templist.sort()
        #print(templist)

        ## Calculate the prior probabilities of each codon for each tag separately.
        def calculateTFIDF(codonPrevalenceDict,tagsKey,codonCount,codonsPerTag,articles):
            tf=dict()
            for tag in tagsKey:
                tf[tag]={}
            for tag in tf:
                for codon in codonPrevalenceDict:
                    #print("TEST: ",len(articles),vocab[codon])
                    tf[tag][codon]=(codonCount[tag][codon]/codonsPerTag[tag])*math.log((1/codonPrevalenceDict[codon]),10)
                    #if tf[tag][codon]<0:
                    #    print(codon)
            return(tf)
        codonPriors=calculateTFIDF(codonPrevalenceDict,tagsKey,words_count_by_screening_code,total_words_num_per_screening_code,articles)
        #def calculateCodonPriorsPerTag(vocab,TagsKey,codonCount,codonsPerTag):
        #    print("Calculating tag prior probabilities...")
        #    d=dict()
        #    vocabLength=(len(vocab))
        #    for i in TagsKey:
        #        d[i]={}
        #    for i in d:
        #        for c in codonCount[i]:
        #            d[i][c]=(  (  codonCount[i][c] +1  )    /   (codonsPerTag[i]   +  vocabLength         ) )

        #codonPriorsPerTag=calculateCodonPriorsPerTag(vocab,tagsKey,words_count_by_screening_code,total_words_num_per_screening_code)
        print("Training complete.\n")
        collected=list()
        collected.append(tagsKey)
        collected.append(tagPriors)
        collected.append(vocab)
        collected.append(codonPriors)
        #print("Codon Priors: ", codonPriors)
        return(collected)
    ## Calculate the relative probabilities of each tag for each abstract.
    def NBTest_codon4(articles,tagsKey,tagPriors,vocab,codonPriorsPerTag):
        print("Calculating probabilities...")
        #print(tagPriors)
        ##create dictionary for the results of the probability calculations.
        r=dict()
        for article in articles:
            r[article.ID]={}
        ## First calculate tag probability based on tag priors.
        for id in r:
            for tag in tagsKey:
                r[id][tag]=tagPriors[tag]
        #print(r)
                #print("ght: ",r[id][tag])
        ## Now multiple that tag probability by the priors for each codon.
        countArticles = len(articles)
        currentCount = 0
        percentDone1=0
        percentDone2=0
        for article in articles:
            for codon in article.codonFourList:
                for tag in tagsKey:
                    if codon in vocab:
                        #print("shagh: ",r[article.ID][tag],codonPriorsPerTag[tag][codon])
                        #r[article.ID][tag]=(r[article.ID][tag])+math.log(codonPriorsPerTag[tag][codon],10)
                        r[article.ID][tag]=r[article.ID][tag]*codonPriorsPerTag[tag][codon]
                    else:
                        continue
                #print(r)
                ##renormalise the probability values after each codon calculation.
                currentProbs=list()
                for tag in r[article.ID]:
                    currentProbs.append(r[article.ID][tag])
                currentSum=sum(currentProbs)
                for tag in r[article.ID]:
                    r[article.ID][tag]=r[article.ID][tag]/currentSum
            #print(r)
            ##keep track of progress
            currentCount=currentCount+1
            percentDone2=((currentCount/countArticles)*100)
            if percentDone2-percentDone1 >5:
                print("    ",int(percentDone2),"%")
                percentDone1=percentDone2
        #print(r)
        return(r)
    NBTrained_codon4=NBTrain_codon4(trainArticles)
    NBtagProbs_codon4=NBTest_codon4(testArticles,NBTrained_codon4[0],NBTrained_codon4[1],NBTrained_codon4[2],NBTrained_codon4[3])
    return(NBtagProbs_codon4)
## Calculate the probability that each article is an IN, based on tag probabilities
## from a method, and a dictionary of which tags are IN or EX. all Probabilities for
## the inputs must sum to 1.
def CalculateProbIN(articles,probDict_codon4,probDict_codon3,probDict_word,probDict_word2,kappaDict,tagAssignmentDict):
    ## Create an dictionary for the IN probability values.
    inDict=dict()
    for ID in probDict_codon4:
        inDict[ID]=0
     ##calculate the inprob for each method
    for ID in probDict_codon4:
        inProb_codon4=0
        inProb_codon3=0
        inProb_word=0
        inProb_word2=0
        for tag in probDict_codon4[ID]:
            if tagAssignmentDict[tag]=="IN":
                inProb_codon4=inProb_codon4+probDict_codon4[ID][tag]
        for tag in probDict_codon3[ID]:
            if tagAssignmentDict[tag]=="IN":
                inProb_codon3=inProb_codon3+probDict_codon3[ID][tag]
        for tag in probDict_word[ID]:
            if tagAssignmentDict[tag]=="IN":
                inProb_word=inProb_word+probDict_word[ID][tag]
        for tag in probDict_word2[ID]:
            if tagAssignmentDict[tag]=="IN":
                inProb_word2=inProb_word2+probDict_word2[ID][tag]
        ##wieght each INprob by the kappa for that method.
        inProb_codon4=inProb_codon4*kappaDict["codon4"]["allTags"]
        inProb_codon3=inProb_codon3*kappaDict["codon3"]["allTags"]
        inProb_word=inProb_word*kappaDict["word"]["allTags"]
        inProb_word2=inProb_word2*kappaDict["word2"]["allTags"]
        ##add up the wieghted inProbs. no need to divide by the sum of the kappas as
        ##this will be the same for all articles. However I will do it anyway so the number
        ## means something
        kappaTotal=kappaDict["codon4"]["allTags"]+kappaDict["codon3"]["allTags"]+kappaDict["word"]["allTags"]+kappaDict["word2"]["allTags"]
        inDict[ID]=((inProb_codon4+inProb_codon3+inProb_word+inProb_word2)/(kappaTotal))
    #print("INdict ",inDict)
    ##Assign that probability to each article
    for article in articles:
        #print("article.ID: ",article.ID)
        #print("INprob: ",inDict[article.ID])
        article.INprob(inDict[article.ID])
##Using the calculated IN probabilities, now rank the articles.
def CalculateProbINrank(articles):
    ##Create a list of all prob values.
    probList=list()
    for article in articles:
        probList.append(article.prob_IN)
    ##sort that list high to low.
    probList.sort(reverse=True)
    ## for each value, look up the corresponding article and assign an INrank
    ## based on the index of the value.
    for pos in range(0,len(probList)):
        for article in articles:
            if article.prob_IN == probList[pos]:
                article.prob_IN_rank=pos+1
## Assign a tag to each novel article based on the probabilities.
def assignSuggestedTag_codon4(tagProbDict,articles):
    print("Assigning 'codon4' method tags...")
    ## For each article get the tag in the probabilities dictionary with the highest
    ## probability value.
    for article in articles:
        tag=max(tagProbDict[article.ID],key=tagProbDict[article.ID].get)
        article.NBcodon4(tag)
#def assignSuggestedTag_codon4_TFIDF(tagProbDict,articles):
    print("Assigning 'codon4_TFIDF' method tags...")
    ## For each article get the tag in the probabilities dictionary with the highest
    ## probability value.
    for article in articles:
        tag=max(tagProbDict[article.ID],key=tagProbDict[article.ID].get)
        article.tag_nb_codon4_TFIDF=tag
def assignSuggestedTag_codon3(tagProbDict,articles):
    print("Assigning 'codon3' method tags...")
    ## For each article get the tag in the probabilities dictionary with the highest
    ## probability value.
    for article in articles:
        tag=max(tagProbDict[article.ID],key=tagProbDict[article.ID].get)
        article.tag_nb_codon3=tag
def assignSuggestedTag_codon4_TFIDF(tagProbDict,articles):
    print("Assigning 'codon4_TFIDF' method tags...")
    ## For each article get the tag in the probabilities dictionary with the highest
    ## probability value.
    for article in articles:
        tag=max(tagProbDict[article.ID],key=tagProbDict[article.ID].get)
        article.tag_nb_codon4_TFIDF=tag
def assignSuggestedTag_word(tagProbDict,articles):
    print("Assigning 'word' method tags...")
    ## For each article get the tag in the probabilities dictionary with the highest
    ## probability value.
    for article in articles:
        tag=max(tagProbDict[article.ID],key=tagProbDict[article.ID].get)
        article.NBword(tag)
#def assignSuggestedTag_word_TFIDF(tagProbDict,articles):
    print("Assigning 'word' method tags...")
    ## For each article get the tag in the probabilities dictionary with the highest
    ## probability value.
    for article in articles:
        tag=max(tagProbDict[article.ID],key=tagProbDict[article.ID].get)
        article.tag_nb_word_TFIDF=tag
def assignSuggestedTag_word2(tagProbDict,articles):
    print("Assigning 'word2' method tags...")
    ## For each article get the tag in the probabilities dictionary with the highest
    ## probability value.
    for article in articles:
        tag=max(tagProbDict[article.ID],key=tagProbDict[article.ID].get)
        article.tag_nb_word2=tag
## Export the assigned tags as a .csv file.
def exportSuggestedTags(articles):
    print("Exporting suggested tag results...")
    ids=["ID"]
    abs=["AbstractText"]
    gtags=["GoldTag"]
    gAssignment=["GoldAssignment"]
    stags_codon4=["suggestedTag_codon4"]
    stags_codon3=["suggestedTag_codon3"]
    #stags_codon4_TFIDF=["suggestedTag_codon4_TFIDF"]
    stags_word=["suggestedTag_word"]
    #stags_word_TFIDF=["suggestedTag_word_TFIDF"]
    stags_word2=["suggestedTag_word2"]
    #stags_suggested=["suggestedTag_resolved"]
    #prob_IN=["probabilityIN"]
    prob_IN_rank=["probabilityINrank"]
    sAssignment=["SuggestedAssignment"]
    reviewT=["ReviewScreening_true"]
    reviewT_random=["ReviewScreening_random?"]
    reviewT_combined=["ReviewScreening_combined"]
    for article in articles:
        ids.append(article.ID)
        gtags.append(article.goldTag)
        gAssignment.append(article.goldAssignment)
        stags_codon4.append(article.tag_nb_codon4)
        stags_codon3.append(article.tag_nb_codon3)
        stags_word.append(article.tag_nb_word)
        #stags_word_TFIDF.append(article.tag_nb_word_TFIDF)
        stags_word2.append(article.tag_nb_word2)
        #stags_codon4_TFIDF.append(article.tag_nb_codon4_TFIDF)
        #stags_suggested.append(article.tag_suggested)
        abs.append(article.content)
        #prob_IN.append(article.prob_IN)
        prob_IN_rank.append(article.prob_IN_rank)
        sAssignment.append(article.assignment_suggested)
        reviewT.append(article.recommendReview)
        reviewT_random.append(article.recommendReview_random)
        if article.recommendReview == True or article.recommendReview_random ==True:
            reviewT_combined.append(True)
        else:
            reviewT_combined.append(False)
    ##Create data columns and create key file.
    rowList=[ids,
        abs,
        gtags,
        gAssignment,
        stags_codon4,
        stags_codon3,
        #stags_codon4_TFIDF,
        stags_word,
        #stags_word_TFIDF,
        stags_word2,
        #stags_suggested,
        #prob_IN,
        prob_IN_rank,
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

## Calculate Cohens kappa coefficient for two lists of tags.
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
## Calculate Cohens kappa coefficient for two lists of tags, for only one of those tags.
def calculateKappa_tag(rList,cList,tag):
    #print("\ntag:",tag)
    def simplifyTags(rList,cList):
        rListSimp=list()
        cListSimp=list()
        for pos in rList:
            if pos ==tag:
                rListSimp.append(tag)
            else:
                rListSimp.append("notTag")
        for pos in cList:
            if pos ==tag:
                cListSimp.append(tag)
            else:
                cListSimp.append("notTag")
        return(rListSimp,cListSimp)
    simpLists=simplifyTags(rList,cList)
    def calculateKappaSimp(rList,cList):
        ##Define variables
        agreeList=list()
        randAgreeProb=0
        tagsKey=list()
        rDict=dict()
        cDict=dict()
        randAgreeDict=dict()
        kappa=0
        ## Simplify lists to only include tag or notTag.

        ##Calculate raw agreement proportion.
        for pos in range(0,len(rList)):
            if rList[pos]==cList[pos]:
                agreeList.append(1)
            else:
                agreeList.append(0)
        #print("agreeList: ",agreeList)
        #print("len(rList): ",len(rList))
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
            randAgreeDict[tag]=rDict[tag]*cDict[tag]
        ##calculate overall probability of agreement by chance.
        for tag in randAgreeDict:
            randAgreeProb=randAgreeProb+randAgreeDict[tag]
        ##Calculate Kappa
        #print("agreeVal: ",agreeVal)
        #print("randAgreeProb: ",randAgreeProb)
        try:
            kappa=(agreeVal-randAgreeProb)/(1-randAgreeProb)
        except:
            kappa=0
        return(kappa)
    kappa=calculateKappaSimp(simpLists[0],simpLists[1])
    #print("kappa: ",kappa)
    return(kappa)
##Calculate the precision of a method for a particular tag.
def calculatePrecision_tag(rList,cList,tag):
    ##Simplify the lists of tags to just tag or notTag.
    def simplifyTags(tagList,tag):
        listSimp=list()
        for pos in tagList:
            if pos == tag:
                listSimp.append(True)
            else:
                listSimp.append(False)
        return(listSimp)
    rListSimp=simplifyTags(rList,tag)
    cListSimp=simplifyTags(cList,tag)
    ## Create variables for ROC calculation values
    tPos=0
    tNeg=0
    fPos=0
    fNeg=0
    TPR=0
    TNR=0
    FPR=0
    for i in range(0,len(cListSimp)):
        if rListSimp[i]==True:
            if cListSimp[i] == True:
                tPos=tPos+1
            else:
                fNeg=fNeg+1
        if rListSimp[i]==False:
            if cListSimp[i] == True:
                fPos=fPos+1
            else:
                tNeg=tNeg+1
    #try:
    #    TPR=tPos/(tPos+fNeg)
    #except:
    #    TPR="NA"
    #try:
    #    FPR=fPos/(fPos+tNeg)
    #except:
    #    FPR="NA"
    try:
        precision= (tPos)/(tPos+fPos)
    except:
        precision=0
    return(precision)
##Set source files for training and testing data.
def reconcileTwoSuggestedTags(articles,kappa_methods_dict):
    ##This function assumes that the suggested tags for each method
    ## have already been assigned to each member of the Article class in the
    ## test object.
    for article in articles:
        ##If the suggested tags from the methods don't match
        if article.tag_nb_codon4 != article.tag_nb_word:
            ##Look up kappa for codon4 tag
            kappa_codon4=kappa_methods_dict["codon4"][article.tag_nb_codon4]
            ##look up kappa for word tag
            kappa_word=kappa_methods_dict["word"][article.tag_nb_word]
            ##calculate which tag-specific kappa is highest
            ##If the kappas are the same then use the tag from the method with
            ## the highest overall kappa.
            if kappa_codon4 == kappa_word:
                tiebreak_codon4=kappa_methods_dict["codon4"]["allTags"]
                tiebreak_word=kappa_methods_dict["word"]["allTags"]
                if tiebreak_codon4>tiebreak_word:
                    article.suggestTag(article.tag_nb_codon4)
                else:
                    article.suggestTag(article.tag_nb_word)
            ##now if codon4 is greater than word
            if kappa_codon4 > kappa_word:
                article.suggestTag(article.tag_nb_codon4)
            ## Now if codon4 is less than word
            if kappa_codon4 < kappa_word:
                article.suggestTag(article.tag_nb_word)
        ##if the suggested tags from the methods do match.
        else:
            article.suggestTag(article.tag_nb_codon4)
## Use the suggested tag within an article, along with the dictionary of tag-assignment
## pairs, to create a suggested assignment for each article.
def AssignmentFromTag(articles,tagAssignmentDict):
    for article in articles:
        #article.INEXassign(tagAssignmentDict[article.tag_suggested])
        #print("test", article.assignment_nb_codon4)
        article.assignment_nb_codon4=tagAssignmentDict[article.tag_nb_codon4]
        article.assignment_nb_codon3=tagAssignmentDict[article.tag_nb_codon3]
        #print("testafter",article.assignment_nb_codon4)
        #article.assignment_nb_codon4="test"
        article.assignment_nb_word=tagAssignmentDict[article.tag_nb_word]
        article.assignment_nb_word2=tagAssignmentDict[article.tag_nb_word2]

def SuggestAssignments(articles):
    print("Making INEX assignments with maximum sensitivity...")
    for article in articles:
        if (article.assignment_suggested=="IN" or article.assignment_nb_codon4=="IN" or article.assignment_nb_codon3=="IN" or article.assignment_nb_word=="IN" or article.assignment_nb_word2=="IN"):
            article.assignment_suggested="IN"
        else:
            article.assignment_suggested="EX"
##Calculate the sensitivity after INEX assignments based on method suggested tags.
def CalculateINEXSensitivity(articles):
    TruePos=0
    gPos=0
    for article in testingArticles:
        if article.goldAssignment == "IN":
            gPos=gPos+1
            if article.assignment_suggested == "IN":
                TruePos=TruePos+1
    maxSenseSensitivity=TruePos/gPos
    return(maxSenseSensitivity)
##Based on the overall suggested INEX tag, mark articles for review that are gold-standard
##EXs and suggested INs.
def MakeReviewRecommendations(articles):
    print("Making article review recommendations based on method tags...")
    k=0
    for article in articles:
        if article.goldAssignment!="IN" and article.assignment_suggested=="IN":
            article.recommendReview=True
            k=k+1
    return(k)
##Makes review recommendations at random, given a desired number.
def MakeReviewRecommendations_random(articles,numReturn):
    ##First set all random recommended reviews to False.
    for article in articles:
        article.recommendReview_random=False
    ##Now assign True values to the appropriate number of articles.
    countArticle=len(articles)
    seed(7)
    posList=list()
    while len(posList)<numReturn:
        value=randint(0,countArticle-1)
        #print(value)
        if articles[value].recommendReview_random==False and articles[value].goldAssignment=="EX":
            articles[value].recommendReview_random=True
            posList.append(value)
    print("Number of random review recommendations made: ",len(posList))


##Based on a user-defined integer, request additional articles for review, based
##on IN probability rank.
def SuggestAdditionalArticlesForReview(articles):
    ##Based on IN assignment probability rankings, assign one more article for review.
    def AddXArticlesForReview(articles,currentNum,requestedNum):
        ##Calculate how many to add.
        toAdd=requestedNum-currentNum
        currentRank=1
        while toAdd>0:
            #print("currentRank: ",currentRank)
            for article in articles:
                if article.prob_IN_rank==currentRank and article.recommendReview==False:
                    ##If the article has a gold assignment of EX and is not currently
                    ##recommended for review, change it's suggested tag to IN and
                    ##recommend it for review. Then break the FOR loop.
                    if article.goldAssignment=="EX":
                        article.assignment_suggested="IN"
                        article.recommendReview=True
                        toAdd=toAdd-1
                        break
                    ##IF the article has a gold assignment of "IN" and is not currently
                    ##recommended for review, change the recommended assignment, but do
                    ##not recommend for review or break the FOR loop.
                    if article.goldAssignment=="IN":
                        article.assignment_suggested="IN"
            currentRank=currentRank+1
    ##Ask the user if they want additional articles.
    requestedNum=int(input("Please specify the total number of articles you would like to receive for review, then press ENTER:"))
    ##Check that the requested number is not higher than the total number of gold excludes.
    def CheckRequestedNum(articles,requestedNum):
        maxReview=0
        for article in articles:
            if article.goldAssignment=="EX":
                maxReview=maxReview+1
        while requestedNum>maxReview:
            print("\nWARNING: Program cannot return more articles for review than there are currently excluded articles. Please enter a number lower than",maxReview)
            requestedNum=int(input("Please enter the total number of articles you would like to receive for review, then press ENTER:"))
        return(requestedNum)
    requestedNum=CheckRequestedNum(articles,requestedNum)
    ##Calculate current number of articles for review.
    k=CountArticlesRecommendedForReview(articles)
    ##If the current number of articles for review is less than the desired number
    ##add another one.
    print("Making additional review recommendation based on method IN assignment probabilities...")
    #print("k: ",k)
    #print("requestedNum: ",requestedNum)
    if requestedNum>k:
        AddXArticlesForReview(articles,k,requestedNum)

##Count the current number of articles recommended for review.
def CountArticlesRecommendedForReview(articles):
    k=0
    for article in articles:
        if article.recommendReview==True:
            k=k+1
    return(k)
##Define a function that takes an articles list object and desired number of return
##articles as inputs and outputs the IDs for that number of articles, chosen at
##random. It should also change the recommend reivew for each article to True.





print("\nPlease enter details for TRAINING dataset.")
trainingArticles=createArticles()
flagDuplicateArticles(trainingArticles)
compareDupArticleTags(trainingArticles)
print("\nPlease enter details for TESTING dataset.")
testingArticles=createArticles()
flagDuplicateArticles(testingArticles)

#for article in trainingArticles:
#    print(article.contentWord2List)

tagAssignmentDict=DefineTagAssignment(trainingArticles,testingArticles)
#print("These are the tag assignments based on the input data:\n",tagAssignmentDict)

##Run the classifying algorithms
NBtagProbs_codon4=NB_codon4(trainingArticles,testingArticles)
NBtagProbs_codon3=NB_codon3(trainingArticles,testingArticles)
NBtagProbs_word=NB_word(trainingArticles,testingArticles)
#NBtagProbs_word_TFIDF=NB_word_TFIDF(trainingArticles,testingArticles)
NBtagProbs_word2=NB_word2(trainingArticles,testingArticles)
#NBtagProbs_codon4_TFIDF=NB_codon4_TFIDF(trainingArticles,testingArticles)
#for article in NBtagProbs_codon4:
#    print("\n",article)
#    print("codon4:\n",NBtagProbs_codon4[article])
#    print("codon4_TFIDF:\n",NBtagProbs_codon4_TFIDF[article])
#    print("word:\n",NBtagProbs_word[article])
#    print("word_TFIDF:\n",NBtagProbs_word_TFIDF[article])
#print("NBtagProbs_codon4_TFIDF: ",NBtagProbs_codon4_TFIDF)

#print(NBtagProbs_codon4_TFIDF)




##Assign the most likely tag
assignSuggestedTag_codon4(NBtagProbs_codon4,testingArticles)
assignSuggestedTag_codon3(NBtagProbs_codon3,testingArticles)
#assignSuggestedTag_codon4_TFIDF(NBtagProbs_codon4_TFIDF,testingArticles)
assignSuggestedTag_word(NBtagProbs_word,testingArticles)
#assignSuggestedTag_word_TFIDF(NBtagProbs_word_TFIDF,testingArticles)
assignSuggestedTag_word2(NBtagProbs_word2,testingArticles)

#for article in testingArticles:
#    print(article.ID,article.tag_nb_codon4_TFIDF)
##Calculate cohens kappa for each classification method, and for tags individually
kappa_methods_dict=dict()
kappa_methods_dict["codon4"]=dict()
kappa_methods_dict["codon3"]=dict()
#kappa_methods_dict["codon4_TFIDF"]=dict()
kappa_methods_dict["word"]=dict()
#kappa_methods_dict["word_TFIDF"]=dict()
kappa_methods_dict["word2"]=dict()
goldTagList=list()
codon4List=list()
codon3List=list()
#codon4TFIDFList=list()
wordList=list()
#wordTFIDFList=list()
word2List=list()
for article in testingArticles:
    goldTagList.append(article.goldTag)
    codon4List.append(article.tag_nb_codon4)
    codon3List.append(article.tag_nb_codon3)
#    codon4TFIDFList.append(article.tag_nb_codon4_TFIDF)
    wordList.append(article.tag_nb_word)
#    wordTFIDFList.append(article.tag_nb_word_TFIDF)
    word2List.append(article.tag_nb_word2)
##First add the overall kappa for each method.
kappa_methods_dict["codon4"]["allTags"]=calculateKappa(goldTagList,codon4List)
kappa_methods_dict["codon3"]["allTags"]=calculateKappa(goldTagList,codon3List)
#kappa_methods_dict["codon4_TFIDF"]["allTags"]=calculateKappa(goldTagList,codon4TFIDFList)
kappa_methods_dict["word"]["allTags"]=calculateKappa(goldTagList,wordList)
#kappa_methods_dict["word_TFIDF"]["allTags"]=calculateKappa(goldTagList,wordTFIDFList)
kappa_methods_dict["word2"]["allTags"]=calculateKappa(goldTagList,word2List)

print("\nComparing suggestion kappas")
print("codon4: ",kappa_methods_dict["codon4"]["allTags"])
print("codon3: ",kappa_methods_dict["codon3"]["allTags"])
#print("codon4_TFIDF: ",kappa_methods_dict["codon4_TFIDF"]["allTags"])
print("word: ",kappa_methods_dict["word"]["allTags"])
#print("word_TFIDF: ",kappa_methods_dict["word_TFIDF"]["allTags"])
print("word2: ",kappa_methods_dict["word2"]["allTags"])
#if hybridMethod==1:
#    print("kappaHybrid: ",hybridKappa)
#else:
#    print("precisionHybrid: ",hybridKappa)
#print("codon4 INEX kappa: ",codon4_INEX_kappa)
#print("word INEX kappa: ",word_INEX_kappa)
#print("word2 INEX kappa: ",word2_INEX_kappa)
#print("hybrid INEX kappa: ",hybrid_INEX_kappa)


##Then add the kappa for each tag for each method.
#tagList=[]
#for article in trainingArticles:
#    tagList.append(article.goldTag)
#tagList=list(set(tagList))


##reconcile tags to produce a single recommended tag, using kappa. Default to using
##tags from the method with the highest overall kappa.
#hybridMethod=1
#for tag in tagList:
#    if hybridMethod==1:
#        kappa_methods_dict["codon4"][tag]=calculateKappa_tag(goldTagList,codon4List,tag)
#        kappa_methods_dict["word"][tag]=calculateKappa_tag(goldTagList,wordList,tag)
#        kappa_methods_dict["word2"][tag]=calculateKappa_tag(goldTagList,word2List,tag)
#    else:
#        kappa_methods_dict["codon4"][tag]=calculatePrecision_tag(goldTagList,codon4List,tag)
#        kappa_methods_dict["word"][tag]=calculatePrecision_tag(goldTagList,wordList,tag)
#        kappa_methods_dict["word2"][tag]=calculatePrecision_tag(goldTagList,word2List,tag)


#print("\nKappa results: \n")
#for tag in kappa_methods_dict["codon4"]:
#    print(kappa_methods_dict["codon4"][tag])
#    print(kappa_methods_dict["word"][tag])

##Reconcile suggested tags. For now this just includes codon4 and word.
#reconcileTwoSuggestedTags(testingArticles,kappa_methods_dict)







## Give each article a recommended IN-EX assignment based on it's recommended
## tag and using the tag-assignment dictionary.
AssignmentFromTag(testingArticles,tagAssignmentDict)
##Make INEX assignments based on the tags of all methods, with maximum sensitivity.
SuggestAssignments(testingArticles)

##Calulate the probability that each article is an IN, based on the tag probabilities
##given as an outputs of the methods.
CalculateProbIN(testingArticles,NBtagProbs_codon4,NBtagProbs_codon3,NBtagProbs_word,NBtagProbs_word2,kappa_methods_dict,tagAssignmentDict)
#for article in testingArticles:
#    print(article.ID,article.prob_IN)
CalculateProbINrank(testingArticles)

##Calculate and print the INEX sensitivity after INEX assignments based on methods
##suggested tags.
INEXsensitivityFromTags=CalculateINEXSensitivity(testingArticles)
print("INEX assignment sensitivity after classifying methods: ",INEXsensitivityFromTags)

##Assign recommendReview to articles based on a gold-standard EX assignment and
##suggested IN assignment.
initialReviewCount=MakeReviewRecommendations(testingArticles)
print("After initial processing,",initialReviewCount,"articles have been flagged for review.")
##Make random review suggestions equal in number to the ones based on the methods.
MakeReviewRecommendations_random(testingArticles,initialReviewCount)

##Ask the user if they want any additional articles for review, and then assign them
##based on the IN assignment probabilities.
#SuggestAdditionalArticlesForReview(testingArticles)
##Count the new number of articles for review.
#print(CountArticlesRecommendedForReview(testingArticles),"articles are now recommended for review.")
#print("INEX assignment sensitivity is now",CalculateINEXSensitivity(testingArticles))

#for article in testingArticles:
#    print("out")
#    print(article.ID,article.goldAssignment,article.assignment_suggested,article.recommendReview,)
#for article in testingArticles:
#    print("test")
#    print(article.ID,article.goldAssignment,article.assignment_suggested)
#    print(article.prob_IN_rank)
#    print(article.recommendReview)
#for article in testingArticles:
#    print("gold: ",article.goldAssignment,"word2: ",article.assignment_nb_word2)
##Calculate the hybrid suggested tags kappa with gold standard
#hybridTagList=list()
#for article in testingArticles:
#    hybridTagList.append(article.tag_suggested)
#hybridKappa=calculateKappa(goldTagList,hybridTagList)

##Calculate kappas for words, codon4, and recommended IN-EX assignments
#goldINEXlist=list()
#codon4INEXlist=list()
#wordINEXlist=list()
#word2INEXlist=list()
#suggestedINEXlist=list()
#for article in testingArticles:
#    goldINEXlist.append(article.goldAssignment)
#    codon4INEXlist.append(article.assignment_nb_codon4)
#    #print(article.ID,article.goldAssignment,article.assignment_nb_codon4)
#    wordINEXlist.append(article.assignment_nb_word)
#    word2INEXlist.append(article.assignment_nb_word2)
#    suggestedINEXlist.append(article.assignment_suggested)
#print(len(goldINEXlist),len(codon4INEXlist),len(wordINEXlist))
#print("INEX lists: ",goldINEXlist,codon4INEXlist,wordINEXlist,suggestedINEXlist)
#for pos in range(0,len(goldINEXlist)):
    #print(goldINEXlist[pos],codon4INEXlist[pos])
#print("calculating codon4 INEX kappa")
#codon4_INEX_kappa=calculateKappa(goldINEXlist,codon4INEXlist)
#word_INEX_kappa=calculateKappa(goldINEXlist,wordINEXlist)
#word2_INEX_kappa=calculateKappa(goldINEXlist,word2INEXlist)
#hybrid_INEX_kappa=calculateKappa(goldINEXlist,suggestedINEXlist)




##Make initial recommendations for articles for review based on goldAssignments and suggestedAssignments.








#for article in testingArticles:
#    print("gold assignment: ", article.goldAssignment)
#    print("suggested assignment: ", article.assignment_suggested)
#    print("recommend review?: ",article.recommendReview)

##Print maximum sensitivity INEX sensitivity.


##Export the results as a csv file.
exportSuggestedTags(testingArticles)

##Report on program runtime.
print("Program took",int(time.time()-startTime),"seconds to run.")

##Prompt to exit program.
input('Press ENTER to exit')

#for article in trainingArticles:
#    print(article.ID)
#    print(len(article.codonFourList))
#    #print(article.codonFourList)
#    print(len(article.codonFourListSet))
#    #print(article.codonFourListSet)
