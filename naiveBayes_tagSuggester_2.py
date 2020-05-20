import time
start = time.time()
import math

##Define training and testing files
trainFile="FibratesTrain.csv"
testFile="FibratesTest.csv"


##TRAINING ALGORITHM
print("Now training the algorithm.")

##define the punctuations to be removed
punctuations = "•™©!£$€/%^&*+±=()â‰¥[]|0123456789'=.,:;?%<>ÿòñ~#@-—–{}úøîæ÷ó¬åà®¯§"+'"“”'
##import the csv module into Python
import csv
##open the csv file containing the training set
#with open(trainFile) as csvfile:
with open(trainFile,encoding="ISO-8859-1") as csvfile:
    readCSV=csv.reader(csvfile,delimiter=',')
    ##create empty lists for abstracts and screening codes
    trainingIDlist=[]
    abstracts=[]
    screening_codes=[]
    ##populate the empty lists with column data by row
    for row in readCSV:
        trainingID=[0]
        abstract=row[1]
        screening_code=row[2]
        ##append the values for abstract and screening code for that row onto
        ##the list of abstracts and screening codes
        trainingIDlist.append(trainingID)
        abstracts.append(abstract)
        screening_codes.append(screening_code)
    #print(abstracts)
    #print(screening_codes)
##remove the first item from the list for abstracts and screening codes
##as this is just the column names
abstracts=abstracts[1:]
screening_codes=screening_codes[1:]
count_all_abstracts=len(abstracts)
print("number of abstracts: ",count_all_abstracts)

##create a list of screening codes without repetition
screening_codes_key=[]
for code in screening_codes:
    if code not in screening_codes_key:
        screening_codes_key.append(code)
#print("screening codes key: ",screening_codes_key)

##create a dictioary of screening codes with the number of abstracts that fall
##into that code.
codes_num=dict()
for c in screening_codes:
    codes_num[c]=codes_num.get(c,0)+1
#print ("Screening codes: ",codes_num)

##create a dictionary of prior probabilites for each screening code.
prior_prob_screening_code=dict()
for c in codes_num:
    prior_prob_screening_code[c]=codes_num[c]/count_all_abstracts
#print("prior probabilities of the screening codes: ",prior_prob_screening_code)

##Create a dictionary of all the words found in the entire training set,
##and a variable of the total number of word positions
##Process the list of abstracts to remove punctuation and make lowercase
all_abstracts_split=[]
all_abstracts_nopunct=[]
#print("abstracts before processing: ",abstracts)
for abstract in abstracts:
    no_punct=""
    for character in abstract:
        if character not in punctuations:
            no_punct= no_punct+character
    all_abstracts_nopunct.append(no_punct)
#print("abstracts after no punctutation: ",all_abstracts_nopunct)
all_abstracts_lower=[]
for abstract in all_abstracts_nopunct:
    all_abstracts_lower.append(abstract.lower())
#print("abstracts after lowercase: ",all_abstracts_lower)

## Check that there are no exact duplicates in the training data after processing
## to remove punctuation and putting into lowercase.
countUniqueAbstracts=len(set(all_abstracts_lower))
print("number of abstracts: ",len(all_abstracts_lower))
print("number of unique abstracts: ",countUniqueAbstracts)
countDupAbstracts=count_all_abstracts - countUniqueAbstracts
if countDupAbstracts > 0:
    print("\nERROR: ",countDupAbstracts," exact duplicate abstract(s) detected in training set.")
    ## Create a dictionary of abstracts, counting up for duplicates
    dupAbstracts=dict()
    for abstract in all_abstracts_lower:
            dupAbstracts[abstract]=dupAbstracts.get(abstract,0)+1
    for abstract in dupAbstracts:
        if dupAbstracts[abstract]>1:
            print ("\nDuplicate Abstract: ",abstract)
            print("Copies of abstract: ",dupAbstracts[abstract])
    print("\nPlease remove ",countDupAbstracts," duplicate abstracts and try again.")
    quit()
else:
    print("No exact duplicate abstracts detected in training set. Continuing training stage.")

##split abstracts into words and put into vocabulary dictionary
##Also count the total number of distinct word positions in this single text document.
total_words_num_all_abstracts=0
vocabulary=dict()
for abstract in all_abstracts_lower:
    split=abstract.split()
    for word in split:
        vocabulary[word]=vocabulary.get(word,0)+1
        total_words_num_all_abstracts=total_words_num_all_abstracts+1
#print("vocabulary: ",vocabulary)
vocabulary_length=len(vocabulary)
print("length of vocabulary: ", vocabulary_length)
print("total word positions in all abstracts: ",total_words_num_all_abstracts)

##Create a master dictionary for the word counts for each screening code
words_count_by_screening_code=dict()
for i in screening_codes_key:
    words_count_by_screening_code[i]={}
#print("words_count_by_screening_code dictionary: ",words_count_by_screening_code)
for i in words_count_by_screening_code:
    for j in vocabulary:
        ## Insert all the words from the vocabulary into each screening code
        ## subdictionary, so that all subdictionaries have the same number of entries.
        words_count_by_screening_code[i][j]=vocabulary[j]*0
#print("words_count_by_screening_code dictionary: ",words_count_by_screening_code)
##For each screening code:
##Create a dictionary of all of the words that eppear in the concatenated text
##document, with the total number of times that they appear
for i in screening_codes_key:
    ##create an empty vector for boolean values
    bool=[]
    ##create an empty list for abstracts text
    abstracts_text=[]
    #compare the code to the screening_codes list to produce a list of true/false
    for j in screening_codes:
        if i==j:
            #print("True")
            bool.append(True)
        else:
            #print("False")
            bool.append(False)
    #print("boolean vectors",bool)
    ##create a variable of the number of true values, i.e. number of abstracts
    ##in that screening class
    abs_num=sum(bool)
    ##for each position in that vector, add the abstract from the list of abstract texts
    ##that corresponds to that position to the string object, but only if the
    ##value corresponding to the same position in bool is True.
    for l in range(0,count_all_abstracts):
        #print(l)
        if bool[l]==True:
            split=all_abstracts_lower[l].split()
            for word in split:
                words_count_by_screening_code[i][word]=words_count_by_screening_code[i][word]+1
#print("words_count_by_screening_code: ",words_count_by_screening_code)

##create a dictionary of the total number of words in all the abstracts of each
##screening code.
total_words_num_per_screening_code=dict()
for i in screening_codes_key:
    total_words_num_per_screening_code[i]={}

for i in screening_codes_key:
    total_words_num_per_screening_code[i]=sum(words_count_by_screening_code[i].values())
#print("total_words_num_per_screening_code: ",total_words_num_per_screening_code)

##Create a dictionary of all the words that appear in the concatenated text
##document, along with their posterior probability. This should be within a second
##master dictionary.
words_PP_by_screening_code=dict()
for i in screening_codes_key:
    words_PP_by_screening_code[i]={}
#print("words_PP_by_screening_code dictionary: ",words_PP_by_screening_code)

##calculate the prior probabilites for each word for each screening code and put
##into the master dictionary words_PP_by_screening_code.
for i in words_PP_by_screening_code:
    for c in words_count_by_screening_code[i]:
        words_PP_by_screening_code[i][c]=(  (  words_count_by_screening_code[i][c] +1  )    /   (total_words_num_per_screening_code[i]   +  vocabulary_length         ) )
#print("words_PP_by_screening_code populated: ",words_PP_by_screening_code)











##CLASSIFYING TASK ALGORITHM
print("\nNow processing novel abstracts.")

##open the csv file containing the novel set
#with open(testFile) as csvfile:
with open(testFile,encoding="ISO-8859-1") as csvfile:
    readCSV_novel=csv.reader(csvfile,delimiter=',')
    ##create empty lists for abstracts and screening codes
    novelIDlist=[]
    novel_abstracts=[]
    gold_screeningCodes=[]
    ##populate the empty lists with column data by row
    for row in readCSV_novel:
        novelID=[0]
        abstract=row[1]
        screening_code=row[2]
        ##append the values for abstract for that row onto
        ##the list of abstracts
        novelIDlist.append(novelID)
        novel_abstracts.append(abstract)
        gold_screeningCodes.append(screening_code)
#print("novel abstracts before processing: ",novel_abstracts)
## Remove the first item of the novel_abstracts list as this is just the column
## header.
novel_abstracts=novel_abstracts[1:]
gold_screeningCodes=gold_screeningCodes[1:]
#print("gold standard screening codes list: ",gold_screeningCodes)
##create a dictioary of screening codes with the number of abstracts that fall
##into that code.
novelCodesNum=dict()
for c in gold_screeningCodes:
    novelCodesNum[c]=novelCodesNum.get(c,0)+1
## Compare the screening codes for the training dataset to the screening codes
## for the testing dataset to make sure that no codes appear in the testing set
## that weren't in the training set
gold_screeningCodes_key=set(gold_screeningCodes)
k=0
for code in gold_screeningCodes_key:
    if code not in screening_codes_key:
        k=1
if k==1:
    print("Error, a screening code is present in the testing dataset that was not present in the training dataset.\nThe program will now close.")
    quit()
else:
    print("All screening codes in testing dataset were present in training dataset.\nThe program will now continue.")
## Create an empty dictionary for the abstract dictionary of gold-standard
## boolean values of screening codes.
goldBoolean=dict()
## Within this dictionary create a sub-dictionary for each screening code.
for i in screening_codes_key:
    goldBoolean[i]=list()
##create a boolean vector for each screening code from the screening codes key
for i in screening_codes_key:
    for j in gold_screeningCodes:
        if i == j:
            goldBoolean[i].append(True)
        else:
            goldBoolean[i].append(False)
#print("goldBoolean dictionary: ",goldBoolean)
##process to remove punctuation and make lowercase
all_abstracts_split=[]
all_abstracts_nopunct=[]
for abstract in novel_abstracts:
    no_punct=""
    for character in abstract:
        if character not in punctuations:
            no_punct= no_punct+character
    all_abstracts_nopunct.append(no_punct)
#print("novel abstracts after no punctutation: ",all_abstracts_nopunct)
novel_abstracts_lower=[]
for abstract in all_abstracts_nopunct:
    novel_abstracts_lower.append(abstract.lower())
#print("novel abstracts after lowercase: ",novel_abstracts_lower)

## Check that there are no exact duplicates in the training data after processing
## to remove punctuation and putting into lowercase.
countUniqueNovelAbstracts=len(set(novel_abstracts_lower))
print("number of abstracts: ",len(novel_abstracts_lower))
print("number of unique abstracts: ",countUniqueNovelAbstracts)
countDupNovelAbstracts=len(novel_abstracts_lower) - countUniqueNovelAbstracts
if countDupNovelAbstracts > 0:
    print("\nERROR: ",countDupNovelAbstracts," exact duplicate abstract(s) detected in testing set.")
    ## Create a dictionary of abstracts, counting up for duplicates
    dupNovelAbstracts=dict()
    for abstract in novel_abstracts_lower:
            dupNovelAbstracts[abstract]=dupNovelAbstracts.get(abstract,0)+1
    ## convert the dictionary to a list and then rank by value.
    l=list()
    for key,val in dupNovelAbstracts.items():
        l.append((val,key))
    #sort greatest to smallest
    l.sort(reverse=True)
    for i in range(0,countDupNovelAbstracts):
        print("\nDuplicate Abstract: ")
        print(l[i])
    print("\nPlease remove duplicate abstracts and try again.")
    quit()
else:
    print("No exact duplicate abstracts detected in testing set. Continuing testing stage.")

##create a dictionary of dictionaries to hold the results
results=dict()
for i in novel_abstracts_lower:
    results[i]={}
#print("empty results dictionary: ",results)
##Compare each abstract against each screening class
##create a dictionary to contain the product of probabiilties for each
##screening code for this novel abstract.

##populate the results dictionary screening code subdictionaries with the abstracts as keys.
## We are using logs to prevent probabilities from tending to 0.
for abstract in novel_abstracts_lower:
    for screeningcode in screening_codes_key:
        results[abstract][screeningcode]=math.log(prior_prob_screening_code[screeningcode],10)
#print("results with screening codes as keys: ",results)
##compute the product of the prior probabilities for each word
for abstract in novel_abstracts_lower:
    #print("abstract text: ",abstract)
    split=abstract.split()
    #print("abstract text split: ",split)
    ##look up the posterior probability for each word in the novel abstract.
    for word in split:
        #print("current word: ",word)
        for screeningcode in words_PP_by_screening_code:
            if word in vocabulary:
                results[abstract][screeningcode]=(results[abstract][screeningcode])+math.log(words_PP_by_screening_code[screeningcode][word],10)
            else:
                continue


## output the relative probability values as a proportion of 1 so that they sum
## to 1 for each abstract.
for abstract in results:
    k=[]
    for c in results[abstract]:
        k.append(results[abstract][c])
    sumlist=sum(k)
    for c in results[abstract]:
        results[abstract][c]=1-(results[abstract][c]/sumlist)
#print("results: ",results)

##Define a dictionary of the test abstracts along with the suggested tags.
suggestedTagsDict=dict()
for abstract in results:
    suggestedTagsDict[abstract]={}
#print("suggestedTagsDict: ",suggestedTagsDict)



for abstract in results:
    suggestedTagsDict[abstract]['suggestedTag']=max(results[abstract], key=results[abstract].get)
#for i in range(0,len(gold_screeningCodes)):
#    suggestedTagsDict[i]['goldTag']=gold_screeningCodes[i]
#print(suggestedTagsDict)
##Create a dictionary of the abstracts and gold-standard screening codes.
goldTagsDict=dict()
for i in range (0,len(novel_abstracts_lower)):
    goldTagsDict[novel_abstracts_lower[i]]=gold_screeningCodes[i]
#print("goldTagsDict: ",goldTagsDict)
##add the gold standard tags to the suggested tags dictionary.
for abstract in suggestedTagsDict:
    suggestedTagsDict[abstract]['goldTag']=goldTagsDict[abstract]
#print("suggestedTagsDict: ",suggestedTagsDict)


##Save a csv file with the abstract, the gold standard tag, and the output
##Suggested tag.
print("Writing reults to .csv file...")
import csv
import itertools
import sys

fields =['abstract','suggestedTag','goldTag']

with open(testFile+"_suggestedTags.csv","w",newline='',encoding="ISO-8859-1") as f:
    w = csv.DictWriter(f,fields)
    w.writeheader()
    for k in suggestedTagsDict:
        w.writerow({field:suggestedTagsDict[k].get(field) or k for field in fields})
print("Done.")

print("Program took",time.time()-start,"seconds to run.")


quit()
## Write the relative probabilities to csv file.
##write the results to csv
print("Writing reults to .csv file...")
import csv
import itertools
import sys

fields=['abstract']
for code in screening_codes_key:
    fields.append(code)
print(fields)

with open(testFile+"_OUTPUT_relativeProbabilities.csv","w",newline='') as f:
    w = csv.DictWriter(f,fields)
    w.writeheader()
    for k in results:
        w.writerow({field:results[k].get(field) or k for field in fields})
print("Done.")
