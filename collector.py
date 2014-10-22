import json
import requests
import re
from lxml import html
from BeautifulSoup import BeautifulSoup


####################
# USA UNIVERSITIES #
####################
print "Importing American Universities"

USA_UNIVERSITIES_PAGE = "http://doors.stanford.edu/universities.html"

page = requests.get(USA_UNIVERSITIES_PAGE)
text = page.text
soup = BeautifulSoup(text)
body = soup.html.body
ol = body.ol
domain_regex = "^.*\((?P<domain>[\s\S]*)\).*$"
h = re.compile(domain_regex)

univ_list = list()
for li in ol:
    try:
        bundle = {
            "web_page": li.a["href"],
            "name": str(li.a.find(text=True)).strip(),
            "domain": h.match(str(li).replace("\n", "").replace("\t", "")).groupdict().get("domain"),
            "country": "USA"
        }
        univ_list.append(bundle)
    except:
        pass

######################
# OTHER UNIVERSITIES #
######################

OTHER_UNIVERSITIES_PAGE = "http://univ.cc/world.php"

page = requests.get(OTHER_UNIVERSITIES_PAGE)
text = page.text
soup = BeautifulSoup(text)
body = soup.html.body
options = body.form.select.findAll("option")

countries = list()
for option in options:
    data = {
        "code": option["value"],
        "country_name": str(option.find(text=True))[:str(option.find(text=True)).find("(")].strip()
    }
    countries.append(data)

countries = countries[1:] # Remove world.

# Now we have the list.
# start import one by one.

detail_url_template = "http://univ.cc/search.php?dom=%s&key=&start=1"


def scan_page(url, country):
    print "Starting the scanning of %s" % country
    print detail_url
    page = requests.get(url)
    text = page.text
    soup = BeautifulSoup(text)
    body = soup.html.body

    for li in body.ol:
        link = li.a["href"]
        domain = link.replace("http://", "").replace("www.", "").strip()
        domain = domain[:domain.find("/")]
        bundle = {
            "web_page": link,
            "name": str(li.a.find(text=True)).strip(),
            "domain": domain,
            "country": country,
        }
        univ_list.append(bundle)
    a_list = re.findall(r"<a.*?\s*href=\"(.*?)\".*?>(.*?)</a>", str(body))
    try:
        next_url = [item[0] for item in a_list if item[1] == " [&gt;&gt;Next]"][0].replace("&amp;", "&")
    except:
        next_url = None
    if next_url:
        url = "http://univ.cc/" + next_url
        print "Next page: %s" % next_url
        scan_page(url, country)

for country_bundle in countries:
    detail_url = detail_url_template % country_bundle.get("code")
    scan_page(detail_url, country_bundle.get("country_name"))

print "Writing files to disk"

with open('world_universities_and_domains.json', 'w') as outfile:
  json.dump(univ_list, outfile)