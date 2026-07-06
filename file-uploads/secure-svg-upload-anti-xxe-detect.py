from lxml import etree

def xxe_scan(filename):

    unsafe_parser = etree.XMLParser(
            resolve_entities=True, 
            load_dtd=True, 
            no_network=False
        )

    tree = etree.parse(filename, parser=unsafe_parser)

    doctype = tree.docinfo
    print(doctype.doctype)



if __name__ == "__main__":
    xxe_scan("ignored_data/malicious.svg")