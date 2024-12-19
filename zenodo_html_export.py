import requests
from bs4 import BeautifulSoup

# URL der Zenodo-API für die gewünschte Community
ZENODO_API_URL = "https://zenodo.org/api/records"
COMMUNITY_ID = "autotechagil"  # ENTER YOUR COMMUNITY ID HERE

def fetch_publications():
    # Abrufen der Veröffentlichungen von der API
    params = {'communities': COMMUNITY_ID,
              'size': 1000,
              'sort': 'mostrecent'}
    response = requests.get(ZENODO_API_URL, params=params)
    
    if response.status_code == 200:
        return response.json()['hits']['hits']
    else:
        print("Error requesting data:", response.status_code)
        return []

def generate_html(publications):

    table_1 = "<table><thead>"
    table_2_de = """<tr>
                    <th>Datum</th>
                    <th>Titel</th>
                    <th>Autor(en)</th>
                    <th>Veranstaltung / Herausgeber</th>
                    <th>Verlinkungen</th>
                    </tr></thead><tbody>"""
    table_2_en = """<tr>
                    <th>Date</th>
                    <th>Title</th>
                    <th>Author(s)</th>
                    <th>Conference / Publisher</th>
                    <th>Links</th>
                    </tr></thead><tbody>"""
    
    table_3 = ""

    for pub in publications:
        doi = pub['doi']
        doi_url = pub['doi_url']
        title = pub['title']
        zenodo_url = pub['links']['self_html']
        description = pub['metadata']['description']
        creators = ""
        creators_zenodo = pub['metadata']['creators']
        for i in range(len(creators_zenodo)):
            creator = creators_zenodo[i]
            if i > 0:
                creators += "; "
            creators += f"{creator['name']} ({creator['affiliation']})"
            if i > 1:
                creators += "; et al."
                break

        publication_date = pub['metadata']['publication_date']
        publisher = ""
        if 'journal' in pub['metadata']:
            journal = pub['metadata']['journal']
            publisher = f"{journal['title']}"
            if 'volume' in journal:
                publisher += f", vol. {journal['volume']}"
            if 'issue' in journal:
                publisher += f", issue {journal['issue']}"
            if 'pages' in journal:
                publisher += f", pp. {journal['pages']}"
        elif 'meeting' in pub['metadata']:
            conference = pub['metadata']['meeting']
            publisher = f"{conference['title']}"
            if 'acronym' in conference:
                publisher += f" ({conference['acronym']})"
            if 'place' in conference:
                publisher += f", {conference['place']}"
            if 'dates' in conference:
                publisher += f", {conference['dates']}"
        else:
            publisher = ""

        table_3 += f"""<tr>
                        <td>{publication_date}</td>
                        <td>{title}</td>
                        <td>{creators}</td>
                        <td>{publisher}</td>
                        <td><p><a href=\"{doi_url}\" target=\"_blank\" rel=\"noopener\">{doi}</a></p><p><a href=\"{zenodo_url}\" target=\"_blank\" rel=\"noopener\">Zenodo</a></p></td>
                   </tr>"""

    table_4 = "</tbody></table>"

    html_doc_de = BeautifulSoup("<html><head><title>Veröffentlichungen</title></head><body></body></html>", 'html.parser')    
    html_doc_de.body.append(html_doc_de.new_tag('h1'))
    html_doc_de.body.h1.string = "Veröffentlichungen"
    item_tag_de = html_doc_de.new_tag('div')
    item_tag_de.append(BeautifulSoup(table_1 + table_2_de + table_3 + table_4, 'html.parser'))
    html_doc_de.body.append(item_tag_de)

    html_doc_en = BeautifulSoup("<html><head><title>Publications</title></head><body></body></html>", 'html.parser')    
    html_doc_en.body.append(html_doc_de.new_tag('h1'))
    html_doc_en.body.h1.string = "Publications"
    item_tag_en = html_doc_en.new_tag('div')
    item_tag_en.append(BeautifulSoup(table_1 + table_2_en + table_3 + table_4, 'html.parser'))
    html_doc_en.body.append(item_tag_en)

    return str(item_tag_de.table), str(item_tag_en.table)

def main():
    publications = fetch_publications()
    
    if publications:
        html_content_de, html_content_en = generate_html(publications)
        
        with open("publications_de.html", "w", encoding="utf-8") as file:
            file.write(html_content_de)
        with open("publications_en.html", "w", encoding="utf-8") as file:
            file.write(html_content_en)
        
        print("HTML files successfully created.")
    else:
        print("No publications found.")

if __name__ == "__main__":
    main()