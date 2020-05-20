print("start")
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

iris = load_iris()
X = iris.data
y = iris.target

#print(X)
X_2d=X[:, :2]
#print(len(X_2d))
X_2d=X_2d[y>0]
#print(len(X_2d))




#print(iris)


print(y)
y_2d=y[y>0]
print(y_2d)
y_2d-=1
print(y_2d)

scaler = StandardScaler()
X = scaler.fit_transform(X)
print(X)
