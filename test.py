import pickle
with open("pickled_algos_rus/featuresets.pickle", "rb") as f:
    a = pickle.load(f)

print(len(a))