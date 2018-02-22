'''
#Author: Abdul Azeez Omar
#Date: Feb 2018
#Purpose: A tool that will start with a given URL and extract all links from that webpage.
'''
from bs4 import BeautifulSoup
from urllib import request
import getopt, sys
from urllib.parse import urlparse
from symbol import except_clause

def getHelp():
    print('\nUsage: ' + sys.argv[0] + " targeSite -o save.txt\n")
    print("-h  to get help")
    print("-t --target to assign the target")
    print("-l --limit to limit the search range")
    print("-m --output only the URLs of pages within the domain and not broken")
    print("-o --to save the result in a file\n")
    exit(1)

# extract root domain of an url
def get_root_domain(url):
    r = urlparse(url)
    tmp = r.netloc
    parts = tmp.split('.')
    if len(parts) < 2:
        return None
    
    return parts[-2] + '.' + parts[-1]

# output report to stdout or file
def outputReport(fout, str):
    if fout != None:
        fout.write(str + '\n')
    else:
        print(str)

# request header
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

# process arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], "mht:o:l:", ["help", "ofile=", "limit="])
except getopt.GetoptError:
    print('Wrong argument, use -h to get help')
    exit()


# flags for options
targeSite = None
output2File = False
outFileName = None
limitSearch = False
limitDomain = None
validLinksOnly = False

for name,value in opts:
    if name in ('-h', '--help'):
        getHelp()
    if name in ('-o', '--ofile'):
        output2File = True
        outFileName = value
    if name in ('-l', '--limit'):
        limitSearch = True
        limitDomain = value
    if name in ('-m'):
        validLinksOnly = True
    if name in ('-t'):
        targeSite = value
localLinks = []
foreignLinks = []
visited = []
broken = []

if targeSite == None:
    print('No target website is given, use -h to get help')
    exit(1)

# add the given URL to the local links collection
localLinks.append(targeSite)
# get root domain
rootDomain = get_root_domain(targeSite)


while len(localLinks) != 0:
    tmpLink = localLinks.pop()
    visited.append(tmpLink)
    req = request.Request(tmpLink, headers=hdr)
    try:
        response = request.urlopen(req)
    except:
        broken.append(tmpLink)
        continue
    # read html page
    html_doc = response.read()
    # parse the website
    soup = BeautifulSoup(html_doc, "html.parser")
    # get all links
    for link in soup.find_all('a'):
        newLink = link.get('href')
        newLink = str(newLink)
        if newLink.startswith('http') or newLink.startswith('https'):
            if get_root_domain(newLink) == rootDomain:
                if limitSearch:    
                    # not visited local links
                    if limitDomain in newLink and newLink not in visited:
                        localLinks.append(newLink)
                elif newLink not in visited:
                    localLinks.append(newLink)
            # foreign link
            else:
                foreignLinks.append(newLink)

fout = None
if output2File:
    fout = open(outFileName, 'w')
# output report
if validLinksOnly:
    for l in visited:
        if l not in broken:
            outputReport(fout, l)
else:
    outputReport(fout, '\n\x1b[6;30;42m' + 'Local links: ' + '\x1b[0m')
    for l in visited:
        if l not in broken:
            outputReport(fout, l + '    OK')
        else:
            outputReport(fout, l + '    BROKEN')
    outputReport(fout, '\n\x1b[6;30;42m' + 'Foreign links: ' + '\x1b[0m')
    for l in foreignLinks:
        outputReport(fout, l)
                
