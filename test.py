##Perform the SVM classification on the data, using the C and gamma parameters
##chosen from the optimisation, and definining the training and testing data
## according the IDs output by the CreateTrainingData function.
def TrainClassifier(dataset,bestParams,IDgroups):
    print("do nothing")

    # Import train_test_split function.
    from sklearn.model_selection import train_test_split

    ##Create X (dimensions array) for training
    X=dataset.Data
    ##Create y (class array) for training
    y=dataset.Target
    ##Create X (dimensions array) for testing
    X=dataset.Data
    ##Create y (class array) for testing

    # Import svm model
    from sklearn import svm

    # Create a svm Classifier. Linear Kernel
    clf = svm.SVC(kernel='rbf',C=bestParams['C'],gamma=bestParams['gamma'])

    #Train the model using the training sets
    clf.fit(X,y)

    #Predict the response for test dataset
    y_pred = clf.predict(X)

    # Import scikit-learn metrics module for accuracy calculation
    from sklearn import metrics

    # Model Accuracy: how often is the classifier correct?
    print("Accuracy: ",metrics.accuracy_score(y,y_pred))

    # Model Precision: what percentage of positively labelled tuples are actually positive?
    print("Precision: ",metrics.precision_score(y,y_pred))

    #Model Recall: What percentage of positive tuples are labelled as positive?
    print("Recall: ",metrics.recall_score(y,y_pred))

    ##Convert the y_pred numpy array to a list.
    y_pred_list=list()
    for item in y_pred:
        y_pred_list.append(item)
    print(y_pred_list)
