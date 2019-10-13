from sklearn import datasets, model_selection, svm, metrics

mnist = datasets.fetch_mldata('MNIST original', data_home='/home/pi/ダウンロード')

print(type(mnist))
print(mnist.keys())