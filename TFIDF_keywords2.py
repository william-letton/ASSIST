## Note start time for testing.
import time
start = time.time()
print("start: ",time.time())

## Define a character list of the punctuations to be removed during processing.
punctuations = "•™©!£$€/%^&*+±=()â‰¥[]|0123456789'=.,:;?%<>ÿòñ~#@-—–{}úøîæ÷ó¬åà®¯§"+'"“”'
## Import the csv module into Python
import csv
import math
## Open the csv file containing the training set, which has the abtstracts in
## column 3 and gold-standard screening codes in column 12.
with open('IMP_AF_1_goldStandard_1000.csv',encoding="ISO-8859-1") as csvfile:
    readCSV=csv.reader(csvfile,delimiter=',')
    ## Create empty lists for abstracts and screening codes
    abstracts=[]
    screening_codes=[]
    ## Populate the empty lists with column data by row
    for row in readCSV:
        abstract=row[2]
        screening_code=row[11]
        ## Append the values for abstract and screening code for that row onto
        ## the list of abstracts and screening codes.
        abstracts.append(abstract)
        screening_codes.append(screening_code)
    #print(abstracts)
    #print(screening_codes)
## Remove the first item from the list for abstracts and screening codes
## aAs this is just the column titles.
abstracts=abstracts[1:]
screening_codes=screening_codes[1:]
count_all_abstracts=len(abstracts)
print("number of abstracts: ",count_all_abstracts)

## Process the list of abstracts to remove punctuation and make lowercase
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

## Create a list of screening codes without repetition.
screening_codes_key=[]
for code in screening_codes:
    if code not in screening_codes_key:
        screening_codes_key.append(code)
#print("screening codes key: ",screening_codes_key)

## Create a dictionary with the screening codes as keys and the number of
## abstracts with that screening code as values.
codes_num=dict()
for c in screening_codes:
    codes_num[c]=codes_num.get(c,0)+1
#print ("Screening codes: ",codes_num)

## Split abstracts into words and put into vocabulary list.

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
#print("vocabulary: ",vocabulary)
vocabulary_length=len(vocabulary)
print("length of vocabulary: ", vocabulary_length)



print("start calculating TF values: ",time.time())
## Calculating TF values.
## Create a dictionary to store the total number of words for each screening code.
SCabstractsWordsNum=dict()
## Create a dictionary to store the TF values.
TFdict=dict()
for code in screening_codes_key:
    TFdict[code]={}
    SCabstractsWordsNum[code]=0
#print("TFdict: ",TFdict)
#print("SCabstractsWordsNum: ",SCabstractsWordsNum)
## Insert all the words from the vocabulary into each screening code
## subdictionary, so that all subdictionaries have the same number of entries
for i in TFdict:
    for j in vocabulary:
        TFdict[i][j]=0
#print("TFdict after population from vocabulary: ",TFdict)
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
## For each word in each screening code, divide the number of occurances by the
## total number of words for that screening code.
for code in TFdict:
    for word in TFdict[code]:
        TFdict[code][word]=TFdict[code][word]/SCabstractsWordsNum[code]
#print("TFdict final: ",TFdict)

print("start calculating IDF values: ",time.time())
## Calculate IDF values.
IDFdict=dict()
for word in vocabulary:
    IDFdict[word]=0
print("done setting 0 values: ",time.time())
#print("IDFdict before population: ",IDFdict)





for word in vocabulary:
    for abstract in all_abstracts_lower:
        split=abstract.split()
        if word in split:
            IDFdict[word]=IDFdict[word]+1
    IDFdict[word]=math.log(count_all_abstracts/IDFdict[word],10)
#print("IDFdict after log-scaled inverse : ",IDFdict)






print("start calculating TF-IDF values: ",time.time())
## Calculate TF-IDF values.
## Create a dictionary to store the results.
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
