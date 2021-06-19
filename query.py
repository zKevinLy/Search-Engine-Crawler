# Group Num:    25 
# Name:         Pratyush Muthukumar
# StudentNetID: muthukup
# StudentID:    66495041

# Name:         Kevin Ly
# StudentNetID: yousrenl
# StudentID:    14596472

import io
import re
import ast
import nltk
import math
import json
from numpy import dot
from numpy.linalg import norm

# Parses txt file to create a dict with token keys and lists of postings as values
def txtToDict(f): #returns a dict of list containing docID of word
    importantData = {}
    lines = f.readlines()
    docCount = int(lines[-1])
    for line in lines[:-1]:
        line = line.strip().split()
        key, val= line[0], line[1:]
        importantData[key] = []
        val = ''.join(val)
        vals = val.split('%')
        vals = vals[:-1]
        for postingDict in vals:
            splits = postingDict.split(';')
            splits = splits[:-1]
            pDict = {
                "docID": splits[0],
                "wordFreq": int(splits[1]),
                "indicesOccurance": ast.literal_eval(splits[2]),
                "tags": ast.literal_eval(splits[3]),
                "TFIDF": float(splits[4])
            }
            importantData[key].append(pDict)
    return importantData, docCount

# Word is the user-entered query
# getInfo finds the token in the index and returns a list of the matching postings
def getInfo(importantData, word, path): #gets word info from importantData[word]
    try:
        with open(path + '/bookkeeping.json') as j: # reading from bookkeeping
            data = json.load(j)
            outLinks = []
            docs = []
            invalid = True
            for w in word:
                if w in importantData.keys():
                    invalid = False
                    for val in importantData[w]:
                        if (val["docID"] in data and val["docID"] not in docs):
                            outLinks.append(val)
                            docs.append(val["docID"])
            if (invalid):
                return "Query returned no matching search results"
            else:
                return outLinks              
    # Word doesn't exist as key in database
    except KeyError:
        return "Query returned no matching search results"
    except:
        return "bookkeeping failed"

# Similarly, we look through bigramIndex for matching bigram postings
def bigramGetInfo(bigramIndex, word, path):
    try:
        with open(path + '/bookkeeping.json') as j: # reading from bookkeeping
            data = json.load(j)
            outLinks = []
            docs = []
            invalid = True
            # Calculate bigrams
            bigrams = list(nltk.bigrams(word))
            if bigrams:
                for b in bigrams:
                    token = b[0]+'_'+b[1]
                    if token in bigramIndex.keys():
                        invalid = False
                        for val in bigramIndex[token]:
                            if (val["docID"] in data and val["docID"] not in docs):
                                outLinks.append(val)
                                docs.append(val["docID"])
            if (invalid):
                return "Query returned no matching search results"
            else:
                return outLinks              
    # Word doesn't exist as key in database
    except KeyError:
        return "Query returned no matching search results"
    except:
        return "bookkeeping failed"

# We calculate a aggregate weight based on the following characteristics:
# 1) HTML Tag importance (Required)
# 2) Location of queries within the document based on indices of occurence (EXTRA CREDIT)
def weightsImportance(postingDict):
    # These are the multipliers that we multiply to the overall cosine similarity score
    # These set of weights are for the HTML tag that a token is found in
    importanceWeights = {
        'title': 3.0,
        'h1': 2.5,
        'a': 2.0,
        'h2': 2.0,
        'h3': 1.5,
        'b': 1.25,
        'i': 1.25
    }
    
    weight = 0
    for tag in postingDict['tags']:
        weight += importanceWeights[tag]

    # This is a set of multipliers that is based on the index of occurance within the HTML file
    # These numbers signify the character in the set of HTML text where the token occur
    # The smaller the index number, the higher up the HTML file the index is
    importanceIndex = {
        250: 3.0,
        500: 2.5,
        750: 2.0,
        1000: 1.5,
        1500: 1.25,
        2000: 1.25
    }

    # We look through the inputted postingDict's indices of occurance to add to the weight multiplier
    # based on where the token is located within the HTML text
    for index in postingDict['indicesOccurance']:
        for k,v in importanceIndex.items():
            if index < k:
                weight += v
                break
    return weight        
    
# The main function that calculates the ranking of the search results
# This function takes in the query, the matching postings, the matching bigram postings, the index, the bigramIndex, and the document counts
# It returns a sorted list of matching postings where the first item in the list has the most relevance to the query based on the following characteristics:
# 1) TF-IDF document-query vector cosine similarity score
# 2) Weights from the above function
def calculateRanking(query, matches, bigramMatches, importantData, bigramIndex, docCount, bigramDocCount):
    ranked = []
    # If the query is 1 word, the document and query vectors will be 1D, so we can just rank the results by the TF-IDF in the postings list
    if (len(query) == 1):
        tfidfArr = []
        for doc in matches:
            # We still multiply the TF-IDF by the weights to include information about the HTML tag and the location of the query
            score = weightsImportance(doc) * doc["TFIDF"]
            bundle = (score, doc["docID"])
            tfidfArr.append(bundle)
        tfidfArr = sorted(tfidfArr, reverse=True)
        for val in tfidfArr:
            ranked.append(val[1])
        return ranked

    # If the query is 2 words, we can look through the bigramIndex first to find the TF-IDF scores and rank based on
    # the scores of weights multipled by TF-IDF of the bigram token
    if (len(query) == 2 and len(bigramMatches) > 1 and type(bigramMatches) is list):
        tfidfArr = []
        for doc in bigramMatches:
            score = weightsImportance(doc) * doc["TFIDF"]
            bundle = (score, doc["docID"])
            tfidfArr.append(bundle)
        tfidfArr = sorted(tfidfArr, reverse = True)
        for val in tfidfArr:
            ranked.append(val[1])
        return ranked
    
    # Creating document vectors for cosine similarity
    docVectors = []

    # Create a document vector for every document that contains atleast one word from the query
    # The document vector contains the TF-IDF scores of all words in the query at that document
    # Similar thing is done for bi-grams, and that TF-IDF score at that bigram for that document
    # is added to the TFIDF from the single token index
    for doc in matches:
        docVec = [0]*len(query)
        docIdx = 0
        biIdx = 0
        for w in query:
            for postings in importantData[w]:
                if (postings["docID"] == doc["docID"]):
                    docVec[docIdx] = doc["TFIDF"]
                    break
            docIdx += 1
        bigrams = list(nltk.bigrams(query))
        for b in bigrams:
            token = b[0] + "_" + b[1]
            if token in bigramIndex.keys():
                for posting in bigramIndex[token]:
                    if (posting["docID"] == doc["docID"]):
                        docVec[biIdx] += doc["TFIDF"]
                        break
            biIdx += 1
        normalize = norm(docVec)
        docVec[:] = [x / normalize for x in docVec]
        docVectors.append(docVec)
        

    # We are creating a query vector so that we can calculate the TF-IDF cosine similarity scores
    # Similar to document vectors, we add the TF-IDF results from single token index and bigram index
    # to calculate the query vector element values
    queryVec = [0]*len(query)
    queryIdx = 0
    # Calculate TF-IDF
    for w in query:
        qTF = 1 + math.log10(query.count(w))
        docFreq = len(importantData[w])
        idf = math.log10(docCount/docFreq)
        tfidf = qTF*idf
        queryVec[queryIdx] = tfidf
        queryIdx += 1
    bigrams = list(nltk.bigrams(query))
    biIdx = 0
    for b in bigrams:
        token = b[0] + "_" + b[1]
        if token in bigramIndex.keys():
            biTF = 1 + math.log10(query.count(b[0]) + query.count(b[1]))
            biDF = len(bigramIndex[token])
            biIDF = math.log10(bigramDocCount/biDF)
            biTFIDF = biTF * biIDF
            queryVec[biIdx] += biTFIDF
            biIdx += 1
    qNorm = norm(queryVec)
    queryVec[:] = [x / qNorm for x in queryVec]


    # Once we have created the query vector and the document vectors, we can compute the cosine similarity
    # between the query vector and each of the document vectors
    cosines = []
    idx = 0
    # Loop through all documents to compute cosine similarity           
    for doc in matches:
        # Calculate cosine similarity
        cos_sim = dot(queryVec, docVectors[idx])/(norm(queryVec)*norm(docVectors[idx]))
        # Also calculate the weight from the above function and multiply it to the cosine similarity
        # to get our final score which we will use to rank the results
        score = weightsImportance(doc) * cos_sim
        # We arrange the data as a tuple so we can return the sorted docIDs from best score to worst 
        bundle = (score, doc["docID"])
        cosines.append(bundle)
        idx += 1

    # Sort the cosine scores from best to worst
    cosines = sorted(cosines, reverse=True)

    # Ranked is the final sorted/ranked array of docIDs
    for val in cosines:
        ranked.append(val[1])
        
    return ranked

# This is the function that calls all of the other query functions
# It takes in the path, the query, and the parsed data from the txt files
def inquire(path, word, importantData, docCount, bigramIndex, bigramDocCount):
        result = []
        # We want to calculate the matching docIds to pass to the ranking function for matching
        # tokens in both the single token index and the bigram, if the query has at least two words
        # If not, we can just find the matching docIds from the single token index
        word = word.lower().split()
        bigramOut = []
        # If there are more than two words in the query, we can use the bigram index to help with ranking
        if len(word) >= 2:
            bigramOut = bigramGetInfo(bigramIndex, word, path)
            out = getInfo(importantData, word, path)
        # If it is a single word query, we will find the matching docIds for that token
        else:
            out = getInfo(importantData, word, path)
        # If the query matches something in the indexes, then out will be a list with some elements
        # So as long as it is, we can compute ranking
        if (type(out) is list and len(out) > 0):
            # We want to find the number of words in the query that match the single word index tokens
            # and send only the valid ones to get ranked
            query = []
            for w in word:
                if w in importantData.keys():
                    query.append(w)
            # We calculate ranking and the ranked set of docIDs are stored back in the list
            out = calculateRanking(query, out, bigramOut, importantData, bigramIndex, docCount, bigramDocCount)
            # We now need to convert the docIDs to their URLs, so we can do that quickly by using bookkeeping.json
            with open(path + '/bookkeeping.json') as j:
                data = json.load(j)
            for val in out:
                result.append(data[val])
        # We return the ranked URL list, which will be displayed in the GUI we implemented as extra credit
        return result           


