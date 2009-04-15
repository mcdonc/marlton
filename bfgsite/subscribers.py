import datetime

from repoze.bfg.traversal import model_path

from repoze.folder.interfaces import IFolder

from repoze.lemonade.content import is_content

from bfgsite.catalog import find_catalog

def postorder(startnode):
    def visit(node):
        if IFolder.providedBy(node):
             for child in node.values():
                 for result in visit(child):
                     yield result
        yield node
    return visit(startnode)

def index_content(object, event):
    """ Index content (an IObjectAddedEvent subscriber) """
    catalog = find_catalog(object)
    if catalog is not None:
        for node in postorder(object):
            if is_content(object):
                path = model_path(node)
                docid = catalog.document_map.add(path)
                catalog.index_doc(docid, node)

def unindex_content(object, event):
    """ Unindex content (an IObjectWillBeRemovedEvent subscriber) """
    catalog = find_catalog(object)
    if catalog is not None:
        path = model_path(object)
        num, docids = catalog.search(path=path)
        for docid in docids:
            catalog.unindex_doc(docid)
            catalog.document_map.remove_docid(docid)

def reindex_content(object, event):
    """ Reindex a single piece of content (non-recursive); an
    IObjectModifed event subscriber """
    catalog = find_catalog(object)
    if catalog is not None:
        path = model_path(object)
        docid = catalog.document_map.docid_for_address(path)
        catalog.reindex_doc(docid, object)

def set_modified(object, event):
    """ Set the modified date on a single piece of content
    unconditionally (non-recursive); an IObjectModified event
    subscriber"""
    now = datetime.datetime.now()
    object.modified = now

def set_created(object, event):
    """ Add modified and created attributes to nodes which do not yet
    have them (recursively); an IObjectWillBeAddedEvent subscriber"""
    now = datetime.datetime.now()
    for node in postorder(object):
        if is_content(object):
            if not getattr(node, 'modified', None):
                node.modified = now
            if not getattr(node, 'created', None):
                node.created = now
