from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()  # to access this program across servers
def homePage():
    return render_template("index.html") #home page

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","") #if there is a " " in between our search the replace it with ""
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString #url with the item we are searching
            uClient = uReq(flipkart_url) #open connection and get the HTTP response for our search URL
            flipkartPage = uClient.read() #Load the content into a variable
            uClient.close() #close connection
            flipkart_html = bs(flipkartPage, "html.parser") #pass the html parser to flipkartPage      #bs help to structure the dataset
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"}) #Inspect element from the web page and find this class
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href'] #getting the url for the item from the page so that we can get into the page of that item and fetch data
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser") # parsing the new link that we derived from above
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"}) #Inspect element from the web page and find this class for the comment box

            filename = searchString + ".csv" #creating a csv file to store the data
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text #Fetching the name of the customer

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text #Fetching the rating of the customer


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text  #Fetching the comment heading of the customer

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''}) #Fetching the comment of the customer
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}  #storing the details in dictionary format
                reviews.append(mydict) #appending the details of one item into reviews list
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
