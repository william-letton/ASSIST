##This version will not detect or remove duplicates

import time
startTime = time.time()
import math
import csv
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
    goldDescision=""
    ##variables calculated in classifier methods
    contentNopunctuation=""
    contentWordList=[]
    codonFourList=[]
    tag_nb_codon4=""
    tag_nb_word=""
    tag_suggested=""
    ##inital processing on initialising
    def __init__(self, content, ID, goldTag):
        self.content = content
        self.ID = ID
        self.goldTag=goldTag
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
            l.append(codon)
        self.codonFourList=l
        ##create words from no punctuation version of content.
        l=list()
        split=self.contentNopunctuation.split()
        for word in split:
            l.append(word)
        self.contentWordList=l
    ##Assigning tags
    def NBcodon4(self,nam):
        self.tag_nb_codon4=nam
    def NBword(self,nam):
        self.tag_nb_word=nam
    def suggestTag(self,nam):
        self.tag_suggested=nam
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
    ## Read file and create a list each for IDs, abstracts, and goldTags
    print("Now reading file...")
    with open(trainFile,encoding="ISO-8859-1") as csvfile:
        readCSV=csv.reader(csvfile,delimiter=',')
        ##create empty lists for abstracts and screening codes
        trainingIDlist=[]
        contents=[]
        goldCodes=[]
        ##populate the empty lists with column data by row
        for row in readCSV:
            trainingIDlist.append(row[inputColID])
            contents.append(row[inputColAbstract])
            goldCodes.append(row[inputColGoldTags])
    ##remove the first item from the list for abstracts and screening codes
    ##as this is just the column names
    contents=contents[1:]
    goldCodes=goldCodes[1:]
    trainingIDlist=trainingIDlist[1:]
    ## Create an Article object for each article and store them in an object.
    allArticles=[Article(contents[i],trainingIDlist[i],goldCodes[i]) for i in range(0,len(trainingIDlist))]
    return(allArticles)
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
        print("unique screening tags: ",tagsKey)
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
        print("unique screening tags: ",tagsKey)
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
## Assign a tag to each novel article based on the probabilities.
def assignSuggestedTag_codon4(tagProbDict,articles):
    print("Assigning tags...")
    ## For each article get the tag in the probabilities dictionary with the highest
    ## probability value.
    for article in articles:
        tag=max(tagProbDict[article.ID],key=tagProbDict[article.ID].get)
        article.NBcodon4(tag)
## Assign a tag to each novel article based on the probabilities.
def assignSuggestedTag_word(tagProbDict,articles):
    print("Assigning tags...")
    ## For each article get the tag in the probabilities dictionary with the highest
    ## probability value.
    for article in articles:
        tag=max(tagProbDict[article.ID],key=tagProbDict[article.ID].get)
        article.NBword(tag)
## Export the assigned tags as a .csv file.
def exportSuggestedTags(articles):
    print("Exporting suggested tag results...")
    ids=["ID"]
    abs=["AbstractText"]
    gtags=["GoldTag"]
    stags_codon4=["suggestedTag_codon4"]
    #stags_word=["suggestedTag_word"]
    #stags_suggested=["suggestedTag"]
    for article in articles:
        ids.append(article.ID)
        gtags.append(article.goldTag)
        stags_codon4.append(article.tag_nb_codon4)
        #stags_word.append(article.tag_nb_word)
        #stags_suggested.append(article.tag_suggested)
        abs.append(article.content)
    rowList=[ids,abs,gtags,stags_codon4]#,stags_word,stags_suggested]
    zipRowList=zip(*rowList)
    with open(str(int(startTime))+'output.csv', 'w', newline='',encoding="ISO-8859-1") as file:
        writer=csv.writer(file)
        writer.writerows(zipRowList)
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
        randAgreeDict[tag]=rDict[tag]*cDict[tag]
    ##calculate overall probability of agreement by chance.
    for tag in randAgreeDict:
        randAgreeProb=randAgreeProb+randAgreeDict[tag]
    ##Calculate Kappa
    kappa=(agreeVal-randAgreeProb)/(1-randAgreeProb)
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
print("\nPlease enter details for TRAINING dataset.")
trainingArticles=createArticles()
flagDuplicateArticles(trainingArticles)
compareDupArticleTags(trainingArticles)
print("\nPlease enter details for TESTING dataset.")
testingArticles=createArticles()
flagDuplicateArticles(testingArticles)

##Run the classifying algorithms
NBtagProbs_codon4=NB_codon4(trainingArticles,testingArticles)
#NBtagProbs_word=NB_word(trainingArticles,testingArticles)

##Assign the most likely tag
assignSuggestedTag_codon4(NBtagProbs_codon4,testingArticles)
#assignSuggestedTag_word(NBtagProbs_word,testingArticles)

##Calculate cohens kappa for each classification method, and for tags individually
#kappa_methods_dict=dict()
#kappa_methods_dict["codon4"]=dict()
#kappa_methods_dict["word"]=dict()
#goldTagList=list()
#codon4List=list()
#wordList=list()
#for article in testingArticles:
#    goldTagList.append(article.goldTag)
#    codon4List.append(article.tag_nb_codon4)
#    wordList.append(article.tag_nb_word)
##First add the overall kappa for each method.
#kappa_methods_dict["codon4"]["allTags"]=calculateKappa(goldTagList,codon4List)
#kappa_methods_dict["word"]["allTags"]=calculateKappa(goldTagList,wordList)
##Then add the kappa for each tag for each method.
#tagList=[]
#for article in trainingArticles:
#    tagList.append(article.goldTag)
#tagList=list(set(tagList))
#for tag in tagList:
#    kappa_methods_dict["codon4"][tag]=calculateKappa_tag(goldTagList,codon4List,tag)
#    kappa_methods_dict["word"][tag]=calculateKappa_tag(goldTagList,wordList,tag)
#    kappa_methods_dict["codon4"][tag]=calculatePrecision_tag(goldTagList,codon4List,tag)
#    kappa_methods_dict["word"][tag]=calculatePrecision_tag(goldTagList,wordList,tag)



#print("\nKappa results: \n")
#for tag in kappa_methods_dict["codon4"]:
#    print(tag)
#    print(kappa_methods_dict["codon4"][tag])
#    print(kappa_methods_dict["word"][tag])

##Reconcile suggested tags
#reconcileTwoSuggestedTags(testingArticles,kappa_methods_dict)
##Export the results as a csv file.
exportSuggestedTags(testingArticles)


print("Program took",int(time.time()-startTime),"seconds to run.")

##Calculate the hybrid suggested tags kappa with gold standard
#hybridTagList=list()
#for article in testingArticles:
#    hybridTagList.append(article.tag_suggested)
#hybridKappa=calculateKappa(goldTagList,hybridTagList)

#print("comparing suggestion kappas")
#print("codon4: ",kappa_methods_dict["codon4"]["allTags"])
#print("word: ",kappa_methods_dict["word"]["allTags"])
#print("hybrid: ",hybridKappa)
