##Program requires installatioon of SciKit from https://scikit-learn.org/stable/install.html
##Program demo can be found at https://www.datacamp.com/community/tutorials/svm-classification-scikit-learn-python

#Import scikit-learn dataset library
from sklearn import datasets
#Load dataset
cancer=datasets.load_breast_cancer()


#Print the names of the 13 features
print("Features: ", cancer.feature_names)

#print the label type of cancer ('malignant' 'benign')
print("Labels: ",cancer.target_names)

# print data(feature)shape
print("cancer.data.shape: ",cancer.data.shape)

# Print the cancer data features (top 5 records)
print("cancer.data[0:5]: ",cancer.data[0:5])

print("dir(cancer): ",dir(cancer))
#print("cancer.DESCR: ",cancer.DESCR)
#print(cancer.filename)
print("cancer.target: ",cancer.target)

# Print the cancer labels (0:malignant, 1:benign)
print(cancer.target)

print(len(cancer.target))
print(len(cancer.data))

# Import train_test_split function.
from sklearn.model_selection import train_test_split

# Split dataset into training set and test set. 70% training and 30% test.
x_train, x_test,y_train,y_test=train_test_split(cancer.data,cancer.target,test_size=0.3,random_state=109)
print(len(x_train))
print(len(x_test))
print(len(y_train))
print(len(y_test))

# Import svm model
from sklearn import svm

# Create a svm Classifier. Linear Kernel
clf = svm.SVC(kernel='linear')

#Train the model using the training sets
clf.fit(x_train,y_train)

#Predict the response for test dataset
y_pred = clf.predict(x_test)

# Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics

# Model Accuracy: how often is the classifier correct?
print("Accuracy: ",metrics.accuracy_score(y_test,y_pred))

# Model Precision: what percentage of positively labelled tuples are actually positive?
print("Precision: ",metrics.precision_score(y_test,y_pred))

#Model Recall: What percentage of positive tuples are labelled as positive?
print("Recall: ",metrics.recall_score(y_test,y_pred))
