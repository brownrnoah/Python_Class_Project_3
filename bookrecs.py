from functools import reduce
from operator import mul, itemgetter
from heapq import nlargest
from io import StringIO
from breezypythongui import EasyFrame, EasyDialog

# Read the book data into a list of (author,title) tuples. Do this at the module/file level.
books = [] 
fileReader = open('booklist.txt', 'r')
for line in fileReader:
    books.append(tuple(line.strip().split(',')))
#print(books)
fileReader.close()


# Read the ratings data into a dictionary keyed by each name (converted to lower case). 
# The value for each key is a list of the ratings for that reader, preserving the original order. 
# Do this also at the module level so the data is available when the functions mentioned below are called. 
ratings = {}
fileReader = open('ratings.txt', 'r')
names = []
while True:
    name = fileReader.readline().strip().lower()
    names.append(name)
    if not name:
        break
    scores = fileReader.readline().split()
    intScores = []

    for score in scores:
        intScores.append(int(score))

    ratings[name] = intScores

#print(ratings)



# Write a function dotprod(x,y) 
def dotprod(x, y):
    total = 0

    for i in range(len(x)):
        total += x[i] * y[i]
    
    return total
#print(dotprod([5, 0, -3], [5, 1, 3])) #5 * 5 + 0 * 1 + -3 * 3 = 16


# Compute affinity scores for each user.  Store it in a data structure at the module level. 
affinityScores = {}

def computeAffinityScores():
    for name1 in ratings:
        for name2 in ratings:
            if name1 != name2:
                score = dotprod(ratings[name1], ratings[name2])
                if score > 0:
                    affinityScores[name1] = affinityScores.get(name1, {})
                    affinityScores[name1][name2] = score

computeAffinityScores()
#print(affinityScores)

# Write the friends function, which returns a sorted list of the names of the two readers with the highest 
# affinity scores compared to the reader in question. Use the sorted function for all sorting in this program. 
def friends(name,nfriends=2):
    '''
        Returns an alphabetized list of the closest friends in reading taste
    '''
    results = affinityScores[name]
    top_n = [name for name,_ in nlargest(nfriends,results.items(),key=itemgetter(1))[:nfriends]]
    return sorted(top_n)

def recommend(name1,nfriends=2):
    '''
        Returns an alphabetized list of books recommended by top friends
    '''
    def aut_title(book):    # Sort key
        aut = book[0].split()
        return (aut[-1],aut[0],book[1])

    read1 = {i for i in range(len(books)) if ratings[name1][i] != 0}        # Books name1 has read
    recs = set()
    for name2 in friends(name1,nfriends):
        liked2 = {i for i in range(len(books)) if ratings[name2][i] > 1}    # Books name2 liked
        recs |= liked2 - read1
    good_books = [books[i] for i in recs]
    return sorted(good_books,key=aut_title)

def report():
    s = StringIO()
    for name in sorted(affinityScores.keys()):
        print(name+':',friends(name),file=s)
        for b in recommend(name):
            print('\t',b,file=s)
        print(file=s)
    return s.getvalue()

#Making a frame to display three buttons that will launch dialog boxes or message boxes.
class BookRecommendations(EasyFrame):
    def __init__(self):
        EasyFrame.__init__(self, 
                            title="Book Recommendations", 
                            width=300, 
                            height=100, 
                            background='powder blue')

        self.friendButton = self.addButton(text='Friends', row=0, column=0, command=self.getFriends)
        self.recommendButton = self.addButton(text='Recommend', row=0, column=1, command=self.getRecommend)
        self.reportButton = self.addButton(text='Report', row=0, column=2, command=self.getReport)
     
    def getFriends(self):
        FriendDialog(self,'Find Friends')
        
    def getRecommend(self):
        RecommendDialog(self, 'Find Recommendations')
        
    def getReport(self):
        self.messageBox("Report",report(),width=70, height = 45)
    
#Dialog box for gathering input and displaying output in a message box.
class FriendDialog(EasyDialog):
    def __init__(self,parent,title):
        EasyDialog.__init__(self,parent,title)

    def body(self,parent):
        self.addLabel(parent,text="Reader:",row=0,column=0)
        self.addLabel(parent,text="# of Friends:",row=1,column=0)
        self.items = self.addListbox(parent,row=0,column=1,width=20,height=3,listItemSelected=self.itemSelected)
        self.itemlist = names
        self.items.insert(0,*self.itemlist)
        self.nfriends = self.addIntegerField(parent,value=2,row=1,column=1,sticky="W")
        self.index = -1
    def itemSelected(self,index):
        self.index = index
    def validate(self):
        if self.index == -1:
            self.messageBox('Error','No selection.')
            return False
        elif int(self.nfriends.get()) < 0:
            self.messageBox("Error","# of friends must be positive.",width=30, height=10)
            return False
        else:
            return True    
        
    def apply(self):
        myString = ""
        for e in friends(self.itemlist[self.index],int(self.nfriends.get())):
            myString += e + "\n"
        self.messageBox("Recommendations for " + str(self.itemlist[self.index]),myString,width=60, height = 15)

#Dialog box for gathering input and displaying output in a message box.
class RecommendDialog(EasyDialog):
    def __init__(self,parent,title):
        EasyDialog.__init__(self,parent,title)

    def body(self,parent):
        self.addLabel(parent,text="Reader:",row=0,column=0)
        self.addLabel(parent,text="# of Friends:",row=1,column=0)
#        self.reader = self.addTextField(parent,"",row=0,column=1)
        self.items = self.addListbox(parent,row=0,column=1,width=20,height=3,listItemSelected=self.itemSelected)
        self.itemlist = names
        self.items.insert(0,*self.itemlist)
        self.nfriends = self.addIntegerField(parent,value=2,row=1,column=1,sticky="W")
        self.index = -1
    def itemSelected(self,index):
        self.index = index
    def validate(self):
        if self.index == -1:
            self.messageBox('Error','No selection.')
            return False
        elif int(self.nfriends.get()) < 0:
            self.messageBox("Error","# of friends must be positive.",width=30, height=10)
            return False
        else:
            return True 

    def apply(self):
        myString = ""
        for e in recommend(self.itemlist[self.index],int(self.nfriends.get())):
            myString += str(e).replace('(','') + "\n"
            myString = myString.replace(')','')
            myString = myString.replace("'",'')
            myString = myString.replace('"','')
            
        self.messageBox("Recommendations for " + str(self.itemlist[self.index]),myString,width=60, height = 15)
    
#All of the above should execute when the module is loaded or imported, 
# so you need to make sure you have computed the friends and affinity scores at the module level, independent of main. 
# Your main function only prints the full report, as previously shown.
def main():
    BookRecommendations().mainloop()
    """Prints reccomendations for all readers """
    with open('recomendations.txt', 'w') as rec_file:
        print(report(), file=rec_file)

if __name__ == '__main__':
    main()
