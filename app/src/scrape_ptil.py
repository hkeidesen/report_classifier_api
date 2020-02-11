import requests
from bs4 import BeautifulSoup
from html.parser import HTMLParser



def find_url_to_all_reportpages():
    # Needed for the header in request 
    headers = {"User-Agent": "Mozilla/5.0"} 
    pages = []
    # i=0 telles the for-loop to start looking at page 0 in the URL that is being given in the for-loop
    i=0
    end_page = 100
    #this for-loop looks for the pagination in the url, and uses BeautifulSoup to retrieve the page numbers
    # the range(1,10) can be increased to include all pages, or just the pages that are of interest.
    print("Getting the number of pages in the URL. This will take some time based on the Internet connection")
    for i in range(1,end_page):

        #the URL that is being used to retrieve all paginated pages
        url = "https://www.ptil.no/tilsyn/tilsynsrapporter/?p="

        #as can be seen in the URL above, no page number is provided, hence "/?p=". The page number is being assigned in the line below
        url = url + str(i)
        #the URL from the previous step is used to .get all the content on the website
        response = requests.get(url, headers=headers)
        #using the built-in html parser, the content from the response is translated to text?  
        soup = BeautifulSoup(response.content,"html.parser")
            #based on the webpage structure, it can be found that the currect pagination page can be found in the class "page-item active" and "li".
            #This is then transformed to .text.

            # Ensuring that if the response code is 200, else it will fail 
        if response.status_code == 200:
            
            #try: except: to catch the error that will be presenting if soup_page_number = soup.find().text fails
            
            try: 
                soup_page_number = soup.find("li", {"class":"page-item active"}).text

                #translated to integer
                soup_page_number = int(soup_page_number)
                print("Appending the current page,", i ,", to the list \"pages\"")
                pages.append(soup_page_number)
                #increases i
                i+=1
            #in this case, an AttributeError will be caught in soup_page_number. Most likely it is becasue there are no more pages to load.    
            except AttributeError: 
                print("End of page reached. Last page is", pages[-1])
                #breaking out of the for-loop when there are no more pages to load.
                break
        else:
            print("An error with the URL casued the program to crash. It can either be the website or the the connection to the website. The server responded with error code", 
                    response.status_code)
            break
        
    return 

## Make soup of webpage
def make_soup(url):
    
    res = requests.get(url)
    soup = BeautifulSoup(res.text,"lxml")

    return soup

def main():
    find_url_to_all_reportpages()
main()