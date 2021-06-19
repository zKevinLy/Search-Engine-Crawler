# Group Num:    25 
# Name:         Pratyush Muthukumar
# StudentNetID: muthukup
# StudentID:    66495041

# Name:         Kevin Ly
# StudentNetID: yousrenl
# StudentID:    14596472

from bs4 import BeautifulSoup
import nltk
import re
import math
import json
import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class HTMLParser:
        def __init__(self):
            # This is the main index used for searching that has individual token keys and a list of postings as values
            self.importantData = {}
            # This is an additional index implemented as part of the bi-gram extra credit part of the assignment
            self.bigramIndex = {}
            self.stopwords = set(stopwords.words('english'))
            # Counting number of unique documents in the index
            self.documentCount = 0
            # Counting number of unique documents in the bigram index
            self.bigramDocumentCount = 0
            
        # Parses a single document based on the docID, which is the file and folder number
        def parseDocument(self, content, folderNo, fileNo):
            """
            Parses a given URL and stores the important data in a dictionary
            Also stores rest of data in a list
             content: raw webpage HTML data
            """
            # These flags help count the number of unique documents in the index and bigram index
            existFlag = False
            existFlagBi = False
            # Create docID object for easier access throughout the search engine
            val = str(folderNo) + "/" + str(fileNo)
            bs = BeautifulSoup(content, "lxml")
                
            # Remove any data that has script or style tags, as they aren't
            # important for the parser
            for unwanted in bs(["script", "style"]):
                unwanted.extract() 

            # HTML tags that are important: <title> (title), <b> (bold),
            # <h1> Heading 1, <h2> Heading 2, <h3> Heading 3, <i> (italics)
            # We also included the <a> (anchor) tag because we index anchor words for the docIDs
            important = bs.findAll(['title','b','h1','h2','h3','i','a'])
            # Initialize NLTK WordNetLemmatizer
            lemmatizer = WordNetLemmatizer()
                
            # Loop through BeautifulSoup extracted data
            for tag in important:
                for t in tag.findAll(text = True):
                    line = ''.join(t)
                    # Tokenize the text to split on nonalphanumeric characters
                    words = re.split('[^a-zA-Z]', line.lower())
                    words = [x for x in words if x]

                    # CREATING INDEX 
                    for w in words:
                        if (len(w) >= 3 and w not in self.stopwords):
                                # Apply lemmatization to tokens
                                token = lemmatizer.lemmatize(w)
                                existFlag = True
                                text = bs.getText().lower()
                                postingDict = {
                                    "docID": val,
                                    "wordFreq": text.count(w),
                                    "indicesOccurance": [m.start() for m in re.finditer(w, text)],
                                }

                                # By getting to this point, the word frequency will atleast have
                                # a value of 1
                                if postingDict["wordFreq"] == 0:
                                        postingDict["wordFreq"] = 1
                                    
                                if (token in self.importantData.keys()):
                                    existingDocs = []
                                    for posting in self.importantData[token]:
                                            existingDocs.append(posting["docID"])
                                    if (val not in existingDocs):                                           
                                            self.importantData[token].append(postingDict)
                                else:
                                    self.importantData[token] = []
                                    self.importantData[token].append(postingDict)
                                    
                                if "tags" not in self.importantData[token][-1].keys():
                                    self.importantData[token][-1]["tags"] = []
                                self.importantData[token][-1]["tags"].append(tag.name)

                    # CREATING BIGRAM INDEX (EXTRA CREDIT)                               
                    # Calculate bigrams to set as the key for the bigram index (Extra Credit)
                    bigrams = list(nltk.bigrams(words))
                    if bigrams:
                        for b in bigrams:
                                # Make sure both portions of the bigram is larger than 3 characters and is not a stopword
                                if (len(b[0]) >= 3 and b[0] not in self.stopwords and len(b[1]) >= 3 and b[1] not in self.stopwords):
                                        token1 = lemmatizer.lemmatize(b[0])
                                        token2 = lemmatizer.lemmatize(b[1])
                                        existFlagBi = True
                                        # In the bigram index, we denote a bigram (word1, word2) as word1_word2 for convenience
                                        token = token1+'_'+token2
                                        text = bs.getText().lower()
                                        # Create a posting that we will place in the array of postings that contains information for ranking
                                        # We can set the docID and calculate the wordFrequency and the locations where a token occurs in a document
                                        postingDict = {
                                                "docID": val,
                                                "wordFreq": text.count(b[0])+text.count(b[1]),
                                                "indicesOccurance": [m.start() for m in re.finditer(b[0], text)] +  [m.start() for m in re.finditer(b[1], text)] ,
                                        }

                                        # By getting to this point, the word frequency will atleast have
                                        # a value of 1
                                        if postingDict["wordFreq"] == 0:
                                                postingDict["wordFreq"] = 1

                                        # We can now add to the list of postings for that token, as long as we already haven't the posting list for the docId already
                                        if (token in self.bigramIndex.keys()):
                                            existingDocs = []
                                            for posting in self.bigramIndex[token]:
                                                    existingDocs.append(posting["docID"])
                                            if (val not in existingDocs):                                           
                                                    self.bigramIndex[token].append(postingDict)
                                        else:
                                            self.bigramIndex[token] = []
                                            self.bigramIndex[token].append(postingDict)

                                        # This is an additional attribute we are adding to the posting that records which tag(s) the token was found inside the document
                                        # We use this for ranking later on, as this gives us information on the HTML tags
                                        if "tags" not in self.bigramIndex[token][-1].keys():
                                            self.bigramIndex[token][-1]["tags"] = []
                                        self.bigramIndex[token][-1]["tags"].append(tag.name)                       

            if existFlag:
                    self.documentCount += 1
            if existFlagBi:
                    self.bigramDocumentCount += 1

        # TF-IDF = [1+log(tf)] * log(N/df)
        def calculateTFIDF(self):
                # importantData dict is now built, so we can retrieve the term and document frequencies
                # to calculate the TF-IDF scores for each term
                for token in self.importantData.keys():
                        # Document frequency is just the length of the postings list
                        docFrequency = len(self.importantData[token])
                        # Calculate Inverse Document Frequency (IDF) for current term
                        idf = math.log10(self.documentCount/docFrequency)
                        # We are creating a new attribute for each posting list that has the TF-IDF score
                        for postingDict in self.importantData[token]:
                                # Term frequency is just wordFreq
                                tf = 1 + (math.log10(postingDict["wordFreq"]))
                                tfidf = tf*idf
                                postingDict["TFIDF"] = tfidf

                # Similarly, we are calculating the TF-IDF score for the bi-gram index for extra credit
                for token in self.bigramIndex.keys():
                        docFrequency = len(self.bigramIndex[token])
                        idf = math.log10(self.bigramDocumentCount/docFrequency)
                        for postingDict in self.bigramIndex[token]:
                                tf = 1 + (math.log10(postingDict["wordFreq"]))
                                tfidf = tf*idf
                                postingDict["TFIDF"] = tfidf
                        
        # Method that calls parseDocument on all docIDs in bookkeeping to create the index if it doesn't exist already
        def parseAll(self, path):
                try:
                        with open(path + '/bookkeeping.json') as j: # reading from bookkeeping
                                data = json.load(j)
                                for identifier in data:
                                        folder_number,file_number = identifier.split("/")
                                        url = data[identifier]
                                        adjustedPath = path + '/' + folder_number + "/" + file_number
                                        try: #skips failed folder/file numbers
                                                with open(adjustedPath) as file:
                                                        print("Parsing " + adjustedPath)
                                                        self.parseDocument(file, folder_number, file_number)
                                        except:
                                                pass
                except:
                    print("bookkeeping failed")
                # Once the index is created, we can calculate TF-IDF for each posting since the document frequency
                # is just the length of the postings list
                self.calculateTFIDF()

        # This stores the index and bigram index into text files so that when we run the search engine, we don't have to parse everything                   
        def storeIndexToFile(self):
                # Writing content of normal index into index.txt
                with open("index.txt", 'w') as f:
                    for key,val in sorted(self.importantData.items(), key = lambda item : len(item[1])):
                        print(key,"", file=f, end= '')
                        for docID in val:
                            for miniFields in docID.values():
                                    print(miniFields,file=f,end=';')
                            print(file=f, end='%')
                        print(file = f)
                    print(self.documentCount, file = f)

                # Writing data of bigramIndex into bigramIndex.txt
                with open("bigramIndex.txt", 'w') as f:
                        for key,val in sorted(self.bigramIndex.items(), key = lambda item : len(item[1])):
                                print(key,"", file=f, end= '')
                                for docID in val:
                                        for miniFields in docID.values():
                                            print(miniFields,file=f,end=';')
                                        print(file=f, end='%')
                                print(file = f)
                        print(self.bigramDocumentCount, file = f)
