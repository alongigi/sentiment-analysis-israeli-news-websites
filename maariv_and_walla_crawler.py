from bs4 import BeautifulSoup
from urllib.request import urlopen

illegal_words = ['vod', 'movies', 'tvshows', 'kid', 'rss', 'about', 'terms', 'cars']

politics_data = {}
parties = set()


def create_parties():
    """
    Populating the parties. The parties set above will include all the name of the parties.
    Populating the politicians. The politicians dictionary above will include all the name of the politicians, when
    the key is the politician name and the value is the party name.
    :return: None
    """
    page = urlopen(
        'https://he.wikipedia.org/wiki/%D7%94%D7%91%D7%97%D7%99%D7%A8%D7%95%D7%AA_%D7%9C%D7%9B%D7%A0%D7%A1%D7%AA_%D7%94%D7%A2%D7%A9%D7%A8%D7%99%D7%9D_%D7%95%D7%90%D7%97%D7%AA')
    soup = BeautifulSoup(page, features="lxml")

    ol_tags = soup.find_all('ol')
    for ol in ol_tags:
        for li in ol.find_all('li'):
            if len(li.find('a').text.split(' ')) > 1:
                polilical_name = li.find('a').text
                party_name = " ".join(
                    li.parent.parent.parent.parent.find_previous_sibling('tr').find('td').find('b').text.split()[1:])

                for name in polilical_name.split(" "):
                    politics_data[name] = party_name

                parties.add(party_name)


def is_relevant_char(char):
    """
    Returns if the char is relevant or not. It is relevant if it a hebrew letter or one of the next labels - ;'."
    :param char: String
    :return:
    """
    rel = set(".'; פםןוטארקשדגכעיחלךףץתצמנהבסז")

    return char in rel


def web(current_level, max_level, url, base_url, news_base_url, relevant_urls, article_page, html_elm_data,
        website_name):
    """
    Handling the crawler logic. if the current url is an article then will operate the handle_article function.
    Otherwise will operate the handle_children function
    :param current_level: The current level of the crawling
    :param max_level:  The max level of the crawling
    :param url: The current url
    :param base_url: The base url
    :param news_base_url: The new base url
    :param relevant_urls: Array which contains the relevant worsds in the url
    :param article_page: A string that shows if the current url is an article or not
    :param html_elm_data: A dictionary which contains data of the html searching data
    :param website_name: The name of the website.
    :return:
    """
    if is_article(url, article_page):
        handle_article(url, html_elm_data, website_name)
    elif current_level <= max_level:
        handle_children(url, base_url, news_base_url, relevant_urls, current_level, max_level, article_page,
                        html_elm_data, website_name)


def get_full_link(link, base_url, news_base_url, website_name):
    """
    Returns the full link of the curent url.
    :param link: Current link
    :param base_url: The base url
    :param news_base_url: url of the news in order to know if it is a news url or not
    :param website_name: The name of the website.
    :return: String
    """
    if "item" in link and news_base_url not in link:
        return news_base_url + link

    if website_name not in link:
        # if base_url not in link:
        link = base_url + link

    return link


def is_relevant_link(link, relevant_urls):
    """
    Responsible for knowing if the curren link is relevant or not. If it does not contains the relevant keyword from
    in the relevant urls for example it is not relevant.
    :param link:
    :param relevant_urls:
    :return: True if the url is relevant, false otherwise.
    """
    if link is None or link == "" or 'javascript' in link:
        return False

    for word in relevant_urls:
        if word in link:
            return True

    return False


def is_article(url, article_page):
    """
    Resposible to return true if it is an article page or false otherwise
    :param url:
    :param article_page:
    :return: true if it is an article page or false otherwise
    """
    return article_page in url and "help" not in url


def get_body_paragraphs(s, html_elm_data):
    """
    Responsible for returning the paragraphs of the page.
    :param s: BeautifulSoup Object
    :param html_elm_data: Dictionary Elements which contains the relevant html elements in the page.
    :return: String[]
    """
    body = s.find(html_elm_data["body"]["tag_name"], {"class": html_elm_data["body"]["class_name"]})

    if body is None:
        return

    paragraphs = body.findAll("p")

    paragraphs = list(map(lambda t: t.text, paragraphs))
    paragraphs = list(map(lambda t: "".join(t.split(",")), paragraphs))

    return paragraphs


def get_sub_title(s, html_elm_data):
    """
    Responsible for returning the sub title of the page.
    :param s: BeautifulSoup Object
    :param html_elm_data: Dictionary Elements which contains the relevant html elements in the page.
    :return: String
    """
    return "".join(s.find(html_elm_data["sub_title"]["tag_name"],
                          {"class": html_elm_data["sub_title"]["class_name"]}).text.split(","))


def get_title(s, html_elm_data):
    """
    Responsible for returning the title of the page.
    :param s: BeautifulSoup Object
    :param html_elm_data: Dictionary Elements which contains the relevant html elements in the page.
    :return: String
    """
    return "".join(s.find(html_elm_data["title"]["tag_name"],
                          {"class": html_elm_data["title"]["class_name"]}).text.split(","))


def get_publish_at(s, html_elm_data):
    """
    Responsible for returning the published date of the page.
    :param s: BeautifulSoup Object
    :param html_elm_data: Dictionary Elements which contains the relevant html elements in the page.
    :return: String
    """
    if html_elm_data["publish_at"]["tag_name"] == "time":
        return s.find(html_elm_data["publish_at"]["tag_name"],
                      {"class": html_elm_data["publish_at"]["class_name"]}).attrs['datetime']
    else:
        return s.find(html_elm_data["publish_at"]["tag_name"],
                      {"class": html_elm_data["publish_at"]["class_name"]}).text


def get_author(s, html_elm_data):
    """
    Responsible for returning the author of the page.
    :param s: BeautifulSoup Object
    :param html_elm_data: Dictionary Elements which contains the relevant html elements in the page.
    :return: String
    """
    return ' '.join(
        s.find(html_elm_data["author"]["tag_name"], {"class": html_elm_data["author"]["class_name"]}).text.split())


def get_kneset_members(paragraph):
    """
    Responsible for returning the kneset members in the paragraph.
    :param paragraph: String
    :return: Kneset members
    """
    parties = set()

    for word in paragraph.split(" "):
        if word in politics_data:
            parties.add(word)

    return "*".join(parties)


def get_parties(paragraph):
    """
    Responsible for returning the parties members in the paragraph.
    :param paragraph: String
    :return: Parties members
    """
    parties = set()

    for word in paragraph.split(" "):
        if word in parties:
            parties.add(word)
        elif word in politics_data:
            parties.add(politics_data[word])

    return "*".join(parties)


def remove_special(str):
    """
    Removes special characters from the
    :param str:
    :return: String with only the relevant characters
    """
    specials = ["\n", "\r", "\n\r", "\r\n", ","]

    for special in specials:
        str = "".join(str.split(special))

    return str


def handle_article(url, html_elm_data, website_name):
    """
    Handles the article page logic. Extracts thepublish the, author, title, sub title, paragraphs, parties and kneset
    members from the page.
    :param url: String
    :param html_elm_data: BountifulSoup Element
    :param website_name: String
    :return: None
    """
    s = get_html(url)
    publish_at = ""
    author = ""
    title = ""
    sub_title = ""
    paragraphs = []

    try:
        sub_title = get_sub_title(s, html_elm_data)
    except:
        pass

    try:
        title = get_title(s, html_elm_data)
    except:
        pass

    try:
        paragraphs = get_body_paragraphs(s, html_elm_data)
    except:
        pass

    try:
        publish_at = get_publish_at(s, html_elm_data)
    except:
        pass

    try:
        author = get_author(s, html_elm_data)
    except:
        pass

    try:
        with open(website_name + "_visited.txt", 'r') as f:
            visited = [line.rstrip('\n') for line in f]

        print(url)
        # print(visited)
        print(url not in visited)

        if url not in visited and paragraphs != None and len(paragraphs) > 0:
            print(url)
            with open(website_name + '.csv', 'a') as fd:
                for i, paragraph in enumerate(paragraphs):
                    if (paragraph.strip() == ""):
                        continue

                    # author, title, sub_title, path, publish_date, paragraph_number ,content, kneset_members, parties
                    fd.write(",".join(
                        [remove_special(author), remove_special(title), remove_special(sub_title),
                         url, publish_at, str(i), remove_special(paragraph), get_kneset_members(paragraph),
                         get_parties(paragraph)]) + "\n")

            visited.append(url)

            with open(website_name + "_visited.txt", 'w') as f:
                for s in visited:
                    f.write(s + '\n')

    except Exception as e:
        print(str(e))


def get_html(url):
    """
    Returns the html from the relevant url.
    :param url: String
    :return: BountifulSoup | None
    """
    try:
        page = urlopen(url)
        return BeautifulSoup(page, "html.parser")
    except:
        return None


def get_children(s, base_url, relevant_urls, news_base_url, website_name):
    """
    Responsible to get the children from the anchors in the current url
    :param s: BountifulSoup
    :param base_url: String
    :param relevant_urls: String[]
    :param news_base_url: String
    :param website_name: String
    :return: String[]
    """
    children = []

    for link in s.findAll('a'):

        link = link.get('href')

        if link is None or "breaking" in link or "tld" in link:
            continue

        link = get_full_link(link, base_url, news_base_url, website_name)

        if is_relevant_link(link, relevant_urls) and " " not in link:
            children.append(link)

    return children


def handle_children(url, base_url, news_base_url, relevant_urls, current_level, max_level, article_page, html_elm_data,
                    website_name):
    """
    Handles the logic of the current children. If the crawler does not get and html from the BountifulSoup than exists
    :param url: String
    :param base_url: String
    :param news_base_url: String
    :param relevant_urls: String[]
    :param current_level: Number
    :param max_level: Number
    :param article_page: String
    :param html_elm_data: Dictionry
    :param website_name: String
    :return:
    """
    s = get_html(url)

    if s is None:
        return

    children = get_children(s, base_url, relevant_urls, news_base_url, website_name)

    for child in children:
        web(current_level + 1, max_level, child, base_url, news_base_url, relevant_urls, article_page, html_elm_data,
            website_name)


create_parties()

# ######################### maariv #########################################3
#
# relevant_urls = ['news', 'breaking-news', 'politics', 'military', 'law', 'israel', 'world', 'elections',
#                  'journalists', 'Author', 'business', 'opinions']
# article_body_div_class_name = {'tag_name': 'div', 'class_name': 'article-details-container'}
# publish_at_div_class_name = {'tag_name': 'span', 'class_name': 'published-at'}
#
# html_elm_data = {
#     "body": {'tag_name': 'div', 'class_name': 'article-body'},
#     "publish_at": {'tag_name': 'span', 'class_name': 'article-publish-date'},
#     "author": {'tag_name': 'span', 'class_name': 'article-reporter'},
#     "title": {'tag_name': 'div', 'class_name': 'article-title'},
#     "sub_title": {'tag_name': 'div', 'class_name': 'article-description'},
# }
# website_name = "maariv"
# article_page = '/Article-'
# # url = 'https://www.maariv.co.il/'
# url = 'https://www.maariv.co.il/'
# news_base_url = 'https://www.maariv.co.il/'
# base_url = 'https://www.maariv.co.il/'
# max_level = 10
# current_level = 0
#
# web(current_level, max_level, url, base_url, news_base_url, relevant_urls, article_page, html_elm_data, website_name)

######################### 13news #########################################3
#
# relevant_urls = ["walla"]
# article_body_div_class_name = {'tag_name': 'div', 'class_name': 'article-details-container'}
# publish_at_div_class_name = {'tag_name': 'span', 'class_name': 'published-at'}
#
# html_elm_data = {
#     "body": {'tag_name': 'section', 'class_name': 'article-content'},
#     "publish_at": {'tag_name': 'time', 'class_name': 'date'},
#     "author": {'tag_name': 'span', 'class_name': 'author with-image'},
#     "title": {'tag_name': 'h1', 'class_name': 'title'},
#     "sub_title": {'tag_name': 'p', 'class_name': 'subtitle'},
# }
# website_name = "walla"
# article_page = 'item'
# url = 'https://www.walla.co.il/'
# base_url = 'https://www.walla.co.il/'
# news_base_url = 'https://news.walla.co.il/'
# max_level = 10
# current_level = 0
#
# web(current_level, max_level, url, base_url, news_base_url, relevant_urls, article_page, html_elm_data, website_name)
