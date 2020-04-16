import nltk
import random
from nltk.classify.scikitlearn import SklearnClassifier
import pickle
from nltk.tokenize import word_tokenize

from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB

from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC

from nltk.classify import ClassifierI
from statistics import mode


class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def classify(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)
        return mode(votes)

    def confidence(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)
        choice_votes = votes.count(mode(votes))
        conf = choice_votes / len(votes)
        return conf


from_russia = open("from_russia.txt", "r").read()
not_from_russia = open("not_from_russia.txt", "r").read()
# move this up here
all_words = []
documents = []

#  j is adject, r is adverb, and v is verb
allowed_word_types = ["J","R","V"]
# allowed_word_types = ["A"]

print("***Processing from_russia words...")
for p in from_russia.split('\n')[:10000]:
    documents.append((p, "from"))
    words = word_tokenize(p)
    pos = nltk.pos_tag(words, lang="rus")
    for w in pos:
        if w[1][0] in allowed_word_types:
            all_words.append(w[0].lower())

print("***Processing not_from_russia words...")
for p in not_from_russia.split('\n')[:10000]:
    documents.append((p, "not_from"))
    words = word_tokenize(p)
    pos = nltk.pos_tag(words, lang='rus')
    for w in pos:
        if w[1][0] in allowed_word_types:
            all_words.append(w[0].lower())


print("***Forming all_words...")

all_words = nltk.FreqDist(all_words)
all_words.plot()
print(list(all_words.keys())[:100])

word_features = list(all_words.keys())[:10000]


def find_features(document):
    words = word_tokenize(document)
    features = {}
    for w in word_features:
        features[w] = (w in words)

    return features


featuresets = [(find_features(rev), category) for (rev, category) in documents]

random.shuffle(featuresets)
print(len(featuresets))
print(5/0)
save_featuresets = open("pickled_algos_rus/featuresets.pickle", "wb")
pickle.dump(featuresets, save_featuresets)
save_featuresets.close()

print("***Coming to a training set...")
testing_set = featuresets[11200:]
training_set = featuresets[:11200]

print("***Coming to NaiveBayesClassifier...")
classifier = nltk.NaiveBayesClassifier.train(training_set)
print("Original Naive Bayes Algo accuracy percent:", (nltk.classify.accuracy(classifier, testing_set)) * 100)
classifier.show_most_informative_features(50)

print("***Saving the NaiveBayesClassifier...")
###############
save_classifier = open("pickled_algos_rus/originalnaivebayes5k.pickle", "wb")
pickle.dump(classifier, save_classifier)
save_classifier.close()

MNB_classifier = SklearnClassifier(MultinomialNB())
MNB_classifier.train(training_set)
print("MNB_classifier accuracy percent:", (nltk.classify.accuracy(MNB_classifier, testing_set)) * 100)

save_classifier = open("pickled_algos_rus/MNB_classifier5k.pickle", "wb")
pickle.dump(MNB_classifier, save_classifier)
save_classifier.close()

BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
BernoulliNB_classifier.train(training_set)
print("BernoulliNB_classifier accuracy percent:", (nltk.classify.accuracy(BernoulliNB_classifier, testing_set)) * 100)

save_classifier = open("pickled_algos_rus/BernoulliNB_classifier5k.pickle", "wb")
pickle.dump(BernoulliNB_classifier, save_classifier)
save_classifier.close()

LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
LogisticRegression_classifier.train(training_set)
print("LogisticRegression_classifier accuracy percent:",
      (nltk.classify.accuracy(LogisticRegression_classifier, testing_set)) * 100)

save_classifier = open("pickled_algos_rus/LogisticRegression_classifier5k.pickle", "wb")
pickle.dump(LogisticRegression_classifier, save_classifier)
save_classifier.close()

LinearSVC_classifier = SklearnClassifier(LinearSVC())
LinearSVC_classifier.train(training_set)
print("LinearSVC_classifier accuracy percent:", (nltk.classify.accuracy(LinearSVC_classifier, testing_set)) * 100)

save_classifier = open("pickled_algos_rus/LinearSVC_classifier5k.pickle", "wb")
pickle.dump(LinearSVC_classifier, save_classifier)
save_classifier.close()

##NuSVC_classifier = SklearnClassifier(NuSVC())
##NuSVC_classifier.train(training_set)
##print("NuSVC_classifier accuracy percent:", (nltk.classify.accuracy(NuSVC_classifier, testing_set))*100)


SGDC_classifier = SklearnClassifier(SGDClassifier())
SGDC_classifier.train(training_set)
print("SGDClassifier accuracy percent:", nltk.classify.accuracy(SGDC_classifier, testing_set) * 100)

save_classifier = open("pickled_algos_rus/SGDC_classifier5k.pickle", "wb")
pickle.dump(SGDC_classifier, save_classifier)
save_classifier.close()
