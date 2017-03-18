# -*- coding:utf-8 -*-
# This script will download all the 10-K, 10-Q and 8-K
# provided that of company symbol and its CIK code.

import os
import errno

import requests
from bs4 import BeautifulSoup
from config import DEFAULT_DATA_PATH

EDGAR_REQUEST_URL = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="


class SecCrawler():
    def __init__(self, output_directory=None):
        self.output = output_directory or DEFAULT_DATA_PATH
        print("Path of the directory where data will be saved: " + self.output)

    def make_directory(self, cik, prior_to, filing_type):
        # Making the directory to save company filings
        path = os.path.join(self.output, cik, filing_type)

        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    print("ERROR in making directory.")
                    raise

    def save_in_directory(
        self, cik, prior_to, doc_list, doc_name_list, filing_type
    ):
        # Save every text document into its respective folder
        for i, base_url in enumerate(doc_list):

            path = os.path.join(
                self.output, cik, filing_type, doc_name_list[i]
            )

            data = requests.get(base_url).text

            with open(path, "ab") as f:
                f.write(data.encode('ascii', 'ignore'))

    def filing_13F(self, cik, prior_to, count):
        try:
            self.make_directory(cik, prior_to, '13-F')
        except Exception as e:
            print(str(e))

        # generate the url to crawl
        base_url = EDGAR_REQUEST_URL + str(cik) + "&type=13F&dateb=" + str(
            prior_to
        ) + "&owner=exclude&output=xml&count=" + str(count)
        print("started 10-Q " + str(cik))
        r = requests.get(base_url)
        data = r.text

        doc_list, doc_name_list = self.create_document_list(data)

        try:
            self.save_in_directory(
                cik, prior_to, doc_list, doc_name_list, '13-F'
            )
        except Exception as e:
            print(str(e))

    def create_document_list(self, data):
        # parse fetched data using BeautifulSoup
        soup = BeautifulSoup(data)
        # store the link in the list
        link_list = list()

        # If the link is .htm convert it to .html
        for link in soup.find_all('filinghref'):
            url = link.string
            if link.string.split(".")[len(link.string.split(".")) -
                                      1] == "htm":
                url += "l"
            link_list.append(url)
        link_list_final = link_list

        print("Number of files to download {0}".format(len(link_list_final)))
        print("Starting download....")

        # List of url to the text documents
        doc_list = list()
        # List of document names
        doc_name_list = list()

        # Get all the doc
        for k in range(len(link_list_final)):
            required_url = link_list_final[k].replace('-index.html', '')
            txtdoc = required_url + ".txt"
            docname = txtdoc.split("/")[-1]
            doc_list.append(txtdoc)
            doc_name_list.append(docname)
        return doc_list, doc_name_list
