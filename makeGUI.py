# Group Num:    25 
# Name:         Pratyush Muthukumar
# StudentNetID: muthukup
# StudentID:    66495041

# Name:         Kevin Ly
# StudentNetID: yousrenl
# StudentID:    14596472

from bs4 import BeautifulSoup 
from tkinter import font
import tkinter as tk 
import requests
import webbrowser
import re
import query

global urlOut
urlOut = []

def callback(event,url):
    webbrowser.open_new(url)

#when hovering over a link, display a snippet of the first paragraph on the page
# This function displays the title and small description of every link if you mouse over the link in the GUI
def on_enter(event, returned, output, link):
    try:
        t = requests.get("http://" + link)
        soup = BeautifulSoup(t.text, 'html.parser')
        x = "TITLE: " + soup.find('title').get_text() + "\n"
        y = "DESCRIPTION: " + soup.get_text() + "\n"
        y = y.split()
        y = [' '.join(y[i:i+10]) for i in range(0, len(y), 10)]
        y = [s + '\n' for s in y[:6]]
        y = ''.join(y)
        x += y
        output.config(text = x)
    except:
        output.config(text = "No Preview Available")

# This is to reset the search bar every time you hit Enter
def on_leave(event, returned, output):
    output.config(text = "")

# This displays the search results by calling query.inquire() and passing in all of the parsed txt data
# Note that parsing the txt files happens once when we start up the search engine, and not at every time we try to query a new word
# Thus, the querying speed of our search engine is fast
def searchResults(entry,path, importantData, docCount, bigramIndex, bigramDocCount):
    request = entry.get() # entry.get() has the input field

    itemFrame = tk.Frame()
    itemFrame.pack()

    output = tk.Label(master= itemFrame,text = "")
    # Create a frame containing the results. 
    # Once searchresults is called again, delete the frame
    if len(request) > 0:
        results = tk.Label(master= itemFrame, text = "Here are your results:")
        results.pack()
        returnedLinks = query.inquire(path,request, importantData, docCount, bigramIndex, bigramDocCount)
        if(returnedLinks != None and len(returnedLinks) > 20):
            results.config(text = "Top 20 results found for '{}':".format(request))
        elif returnedLinks != None:
            results.config(text = "{} result(s) found:".format(len(returnedLinks)))

        if returnedLinks != None:
            for num,l in enumerate(returnedLinks):
                if num < 20:
                    
                    if len(l) > 200:
                        text = l[:200] + "..."
                    else:
                        text = l
                    returned = tk.Label(master= itemFrame,text = text, fg="blue", cursor="hand2")
                    returned.pack()
                    returned.bind("<Button-1>", lambda event,u=l: callback(event, "http://"+u))

                    returned.bind("<Enter>", lambda event,u=l: on_enter(event,returned, output, u))
                    returned.bind("<Leave>", lambda event: on_leave(event,returned, output))

                    f = font.Font(returned, returned.cget("font"))
                    f.configure(underline=True)
                    returned.configure(font=f)
                
                returned =""
            returnedLinksLen = tk.Label(master= itemFrame, text = "Number of links: "+ str(len(returnedLinks)))
            returnedLinksLen.pack(side = tk.RIGHT)
        else:
            results = tk.Label(master= itemFrame,text = "No results were found")
            results.pack()

    
    output.pack() 


    entry.delete(0,tk.END)
    urlOut.append(itemFrame)
    if len(urlOut) > 1:
        urlOut.pop(0).destroy()

    

# special case for Enter and clicking button
def enter(event,entry,path, importantData, docCount, bigramIndex, bigramDocCount):
    searchResults(entry,path, importantData, docCount, bigramIndex, bigramDocCount)

#making the tkinter window
def makeWindow(path, importantData, docCount, bigramIndex, bigramDocCount):
    root = tk.Tk()
    root.title("Simple Search Engine")
    label = tk.Label(master= root, text="Search Engine: ", font = ("New York",25))
    label.pack(side = tk.TOP)

    searchFrame = tk.Frame(master = root)
    searchFrame.pack(side=tk.TOP) 

    label = tk.Label(master= searchFrame, text="Searching: ")
    label.pack(side = tk.LEFT)

    #getting search field
    entry = tk.Entry(master = searchFrame, width = 50)
    entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    entry.pack()
    entry.focus_set()                                           #automatically start typing
    root.bind("<Return>", (lambda event: enter(event,entry, path, importantData, docCount, bigramIndex, bigramDocCount)))   #press enter

    #Enter button
    butt = tk.Button(searchFrame, text='Enter',command = lambda: searchResults(entry,path, importantData, docCount, bigramIndex, bigramDocCount))   
    butt.pack(side=tk.RIGHT)  
            
    
    root.geometry("1080x720")
    root.mainloop()
    
