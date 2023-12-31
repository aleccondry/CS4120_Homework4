# FIRST: RENAME THIS FILE TO sentiment_utils.py 

# YOUR NAMES HERE:
# Alec Condry (4120) and Shrihari Subramaniam (4120)

"""
Felix Muzny
CS 4/6120
Homework 4
Fall 2023

Utility functions for HW 4, to be imported into the corresponding notebook(s).

Add any functions to this file that you think will be useful to you in multiple notebooks.
"""
# fancy data structures
from collections import defaultdict, Counter
# for tokenizing and precision, recall, f_measure, and accuracy functions
import nltk
from nltk.metrics.scores import precision, recall, f_measure, accuracy
# for plotting
import matplotlib.pyplot as plt
# so that we can indicate a function in a type hint
from typing import Callable
nltk.download('punkt')

import numpy as np

def generate_tuples_from_file(training_file_path: str) -> list:
    """
    Generates data from file formated like:

    tokenized text from file: [[word1, word2, ...], [word1, word2, ...], ...]
    labels: [0, 1, 0, 1, ...]
    
    Parameters:
        training_file_path - str path to file to read in
    Return:
        a list of lists of tokens and a list of int labels
    """
    # PROVIDED
    f = open(training_file_path, "r", encoding="utf8")
    X = []
    y = []
    for review in f:
        if len(review.strip()) == 0:
            continue
        dataInReview = review.strip().split("\t")
        if len(dataInReview) != 3:
            continue
        else:
            t = tuple(dataInReview)
            if (not t[2] == '0') and (not t[2] == '1'):
                print("WARNING")
                continue
            X.append(nltk.word_tokenize(t[1]))
            y.append(int(t[2]))
    f.close()  
    return X, y


"""
NOTE: for all of the following functions, we have provided the function signature and docstring, *that we used*, as a guide.
You are welcome to implement these functions as they are, change their function signatures as needed, or not use them at all.
Make sure that you properly update any docstrings as needed.
"""


def generate_lines_from_file(training_file_path: str) -> list:
    """
    Generates data from file formated like:

    tokenized text from file: ["...", "...", ...]
    labels: [0, 1, 0, 1, ...]
    
    Parameters:
        training_file_path - str path to file to read in
    Return:
        a list of lists of tokens and a list of int labels
    """
    # PROVIDED
    f = open(training_file_path, "r", encoding="utf8")
    X = []
    y = []
    for review in f:
        if len(review.strip()) == 0:
            continue
        dataInReview = review.strip().split("\t")
        if len(dataInReview) != 3:
            continue
        else:
            t = tuple(dataInReview)
            if (not t[2] == '0') and (not t[2] == '1'):
                print("WARNING")
                continue
            X.append(t[1])
            y.append(int(t[2]))
    f.close()  
    return X, y

def get_prfa(dev_y: list, preds: list, verbose=False) -> tuple:
    """
    Calculate precision, recall, f1, and accuracy for a given set of predictions and labels.
    Args:
        dev_y: list of labels
        preds: list of predictions
        verbose: whether to print the metrics
    Returns:
        tuple of precision, recall, f1, and accuracy
    """
    tp, tn, fp, fn = 0, 0, 0, 0
    for ref, pred in zip(dev_y, preds):
        if ref == pred == 1:
            tp += 1
        if pred == 1 and pred != ref:
            fp += 1
        if ref == pred == 0:
            tn += 1
        if pred == 0 and pred != ref:
            fn += 1

    prec = tp / (tp + fp)
    acc = (tp + tn) / (tp + tn + fn + fp)
    rec = tp / (tp + fn)
    f1 = (2 * prec * rec) / (prec + rec)

    if verbose:
        print(f"Precision = {prec}")
        print(f"Recall =    {rec}")
        print(f"f1 score =  {f1}")
        print(f"Accuracy =  {acc}")
    return prec, rec, f1, acc

def create_training_graph(metrics, kind, plot_num, savepath=None, verbose=False) -> None:
    """
    Create a graph of the classifier's performance on the dev set as a function of the amount of training data.
    Args:
        metrics: a list of tuples returned from get_prfa in order of least training data to most
        kind: the kind of model being used (will go in the title)
        plot_num: which plot number is being created
        savepath: the path to save the graph to (if None, the graph will not be saved)
        verbose: whether to print the metrics
    """
    x = [percentage for percentage in range(10, 101, 10)]
    plot_labels = ['Precision', 'Recall', 'F1', 'Accuracy']
    for i in range(0, len(metrics[0])):
        y = [metric[i] for metric in metrics]
        plt.plot(x, y, label=plot_labels[i])
    plt.ylim(0, 1)
    plt.xlabel("Percentage of Training Data Used")
    plt.ylabel("Metric's Value")
    plt.title("Percentage of Training Data Used vs Resulting Metrics")
    plt.legend()
    plt.savefig(f"{savepath}plot{plot_num}_{kind}")
    plt.show()


def create_index(all_train_data_X: list) -> list:
    """
    Given the training data, create a list of all the words in the training data.
    Args:
        all_train_data_X: a list of all the training data in the format [[word1, word2, ...], ...]
    Returns:
        vocab: a list of all the unique words in the training data
    """
    # figure out what our vocab is and what words correspond to what indices
    train_flat = []
    for row in all_train_data_X[0]:
        train_flat.extend(row)

    #All tokens from train tuples
    vocab = set(train_flat)
    return list(vocab)


def featurize(vocab: list, data_to_be_featurized_X: list, binary: bool = False, verbose: bool = False) -> np.ndarray:
    """
    Create vectorized BoW representations of the given data.
    Args:
        vocab: a list of words in the vocabulary
        data_to_be_featurized_X: a list of data to be featurized in the format [[word1, word2, ...], ...]
        binary: whether or not to use binary features
        verbose: boolean for whether or not to print out progress
    Returns:
        a list of sparse vector representations of the data in the format [[count1, count2, ...], ...]
    """
    # using a Counter is essential to having this not take forever

    if verbose:
        print(f'Initializing featurization with binary mode set to {binary}')
        
    result = np.empty([len(data_to_be_featurized_X), len(vocab)])

    if verbose:
        print('Starting enumeration of data to be featurized')
    for idx,j in enumerate(data_to_be_featurized_X):
        sample_map = Counter(j)
        
        feature_list = []
        
        for i in vocab:
            if binary == True:
                x = sample_map.get(i, 0)
                feature_list.append(1) if x > 0 else feature_list.append(0)
            else:
                feature_list.append(sample_map.get(i, 0))
            
        if verbose:
            print(f'Adding featurized list for index {idx} from data to be featurized')
        result[idx] = feature_list
    
    return result
