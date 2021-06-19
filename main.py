# Group Num:    25 
# Name:         Pratyush Muthukumar
# StudentNetID: muthukup
# StudentID:    66495041

# Name:         Kevin Ly
# StudentNetID: yousrenl
# StudentID:    14596472

from htmlParser import HTMLParser
import query 
import sys
import makeGUI
import os

if __name__ == "__main__":

    file = "index.txt"
    file2 = "bigramIndex.txt"
    path = sys.argv[1]
    parser = HTMLParser()
    # If the index database doesn't exist, parse the documents to create it
    print("Searching for preloaded index...")
    if not os.path.isfile(file) or not os.path.isfile(file2) or os.path.getsize(file) == 0 or os.path.getsize(file2) == 0:
        print("No preloaded index found. Indexing webpages now...")
        parser.parseAll(path)
        print("Document count: " + str(parser.documentCount))
        print("Bigram document count: " + str(parser.bigramDocumentCount))
        parser.storeIndexToFile()
    print("Preloaded index found. Loading from index...")
    # Read from the index.txt to create an index dict to calculate rankings and return search results
    with open("index.txt", 'r') as f:
        importantData, docCount = query.txtToDict(f)
    # Read from the bigramIndex.txt to create a bigramIndex dict
    with open("bigramIndex.txt", 'r') as f2:
        bigramIndex, bigramDocCount = query.txtToDict(f2)
        
    # GUI: EXTRA CREDIT
    # Open the GUI (implemented with Tkinter)    
    makeGUI.makeWindow(path, importantData, docCount, bigramIndex, bigramDocCount)         
    
