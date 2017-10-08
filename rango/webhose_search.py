import json
import urllib.parse
import urllib.request
import sys
import webhoseio


def read_webhose_key():
    """
    Read the webhose api from a file
    :return: key
    """
    webhose_api_key = None

    try:
        with open('search.key', 'r') as f:
            webhose_api_key = f.readline().strip()

    except:
        raise IOError('search.key file not found')

    return webhose_api_key


def run_query(search_terms, size=10):
    """
    return a list of results from the webhose api
    :param search_terms:
    :param size:
    :return:
    """
    webhose_api_key = read_webhose_key()

    if not webhose_api_key:
        raise KeyError('Webhose key not found')

    root_url = 'http://webhose.io/search'
    query_string = urllib.parse.quote(search_terms)
    search_url = ('{root_url}?token={key}&format=json&q={query}'
                  '&sort=relevancy&size={size}').format(
        root_url=root_url,
        key=webhose_api_key,
        query=query_string,
        size=size)

    results = []
    try:
        response = urllib.request.urlopen(search_url).read().decode('utf-8')
        json_response = json.loads(response)

        for post in json_response['posts']:
            results.append({
                'title': post['title'],
                'link': post['url'],
                'summary': post['text'][:200]
            })

    except:
        print("Error when querying the Webhose API")

    return results


def run_webhose_query(search_terms):
    webhoseio.config(token=read_webhose_key())
    query_params = {
        "q": search_terms,
        "sort": "relevancy",
        "size": 10,
    }
    return webhoseio.query("filterWebContent", query_params)


def ask_search_terms():
    return input("You are going to use Webhose search, please provide search terms as a string. "
                 "All terms should be separated with a whitespace.").split(' ')


def print_titles(query_result):
    titles_and_summaries = []
    for elem in query_result['posts']:
        titles_and_summaries += ["element {} ".format(len(titles_and_summaries) + 1),
                                 "Title : {}\n".format(elem['title']), ]
    return "".join(titles_and_summaries)


def main():
    search_terms = []
    if len(sys.argv) > 1:
        search_terms += sys.argv[1:]
    else:
        search_terms = ask_search_terms()
    search_terms = " ".join(search_terms)

    print(run_webhose_query(search_terms))


if __name__ == "__main__":

    main()
