import pandas as pd
import numpy as np
from sklearn import svm

train_data_contents = """
class_label,x_acc_val
B,1
M,10
C,2
S,23
N,12"""

with open('train.csv', 'w') as output:
    output.write(train_data_contents)

train_dataframe = pd.read_csv('train.csv')



train_labels = train_dataframe.class_label
labels = list(set(train_labels))
train_labels = np.array([labels.index(x) for x in train_labels])
train_features = train_dataframe.iloc[:,1:]
train_features = np.array(train_features)

print "train labels: "
print train_labels
print 
print "train features:"
print train_features


classifier = svm.SVC()
classifier.fit(train_features, train_labels)

test_data_contents = """
x_acc_val
1
10
2
23
12
"""

with open('test.csv', 'w') as output:
    output.write(test_data_contents)

test_dataframe = pd.read_csv('test.csv')

test_features = test_dataframe.iloc[:,0:]
test_features = np.array(test_features)

results = classifier.predict(test_features)

print results