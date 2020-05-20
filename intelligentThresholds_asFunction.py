## This function takes the dictionary of probability results, and the screening
## code to output a list of threshold values to apply for that screening code,
## that has been defined through iteration to find the values of change in TPR
## and FPR
def defineThresholds(dictionary,screeningCode):
    ## Define an initial thresholds list of just 0 and 1.
    thresholdList=[0,0.5,1]
    testList=list()
    goldList=list()
    for x in range(0,30):
        ##Apply the thresholding for each value in thresholdList and store the TPR and
        ##FPR values.
        TPRvalList=list()
        FPRvalList=list()
        for threshold in thresholdList:
            testList=list()
            ## Create variables for ROC calculation values
            tPos=0
            tNeg=0
            fPos=0
            fNeg=0
            TPR=0
            TNR=0
            FPR=0
        for i in dictionary:
            if dictionary[i][screeningCode]>threshold:
                testList.append(True)
            else:
                testList.append(False)

        goldList=goldBoolean[screeningCode]

            for i in range(0,len(testList)):
                if goldList[i]==True:
                    if testList[i] == True:
                        tPos=tPos+1
                    else:
                        fNeg=fNeg+1
                if goldList[i]==False:
                    if testList[i] == True:
                        fPos=fPos+1
                    else:
                        tNeg=tNeg+1
            try:
                TPR=tPos/(tPos+fNeg)
            except:
                TPR="NA"
            try:
                FPR=fPos/(fPos+tNeg)
            except:
                FPR="NA"
            TPRvalList.append(TPR)
            FPRvalList.append(FPR)
        #print("TPRvalList: ",TPRvalList)
        #print("FPRvalList: ",FPRvalList)

        ##compare the FPR and TPR values between thresholds and if there is a difference
        j=list()
        for i in range(1,len(thresholdList)):
            if (TPRvalList[i]!=TPRvalList[i-1]) or (FPRvalList[i]!=FPRvalList[i-1]):
                j.append((thresholdList[i]+thresholdList[i-1])/2)
        #print(j)
        ## Replace the original thresholdList with the new list, sorted
        thresholdList=list(set(thresholdList+j))
        thresholdList.sort()
        #print(thresholdList)
