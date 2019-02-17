import pickle
f = open('latest_examples.exmp', 'rb')
data = pickle.load(f)
print(data)
print(len(data))
f.close()
