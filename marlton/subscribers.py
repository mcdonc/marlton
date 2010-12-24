import datetime

from zope.component import queryAdapter

from pyramid.traversal import resource_path

from repoze.folder.interfaces import IFolder

from repoze.lemonade.content import is_content

from marlton.catalog import find_catalog
from marlton.interfaces import IMetadata

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
                path = resource_path(node)
                docid = catalog.document_map.add(path)
                catalog.index_doc(docid, node)
                adapter = queryAdapter(node, IMetadata)
                if adapter is not None:
                    metadata = adapter()
                    catalog.document_map.add_metadata(docid, metadata)

def unindex_content(object, event):
    """ Unindex content (an IObjectWillBeRemovedEvent subscriber) """
    catalog = find_catalog(object)
    if catalog is not None:
        path = resource_path(object)
        num, docids = catalog.search(path=path)
        for docid in docids:
            catalog.unindex_doc(docid)
            catalog.document_map.remove_docid(docid)

def reindex_content(object, event):
    """ Reindex a single piece of content (non-recursive); an
    IObjectModifed event subscriber """
    catalog = find_catalog(object)
    if catalog is not None:
        path = resource_path(object)
        docid = catalog.document_map.docid_for_address(path)
        catalog.reindex_doc(docid, object)
        catalog.document_map.remove_metadata(docid)
        adapter = queryAdapter(object, IMetadata)
        if adapter is not None:
            metadata = adapter()
            catalog.document_map.add_metadata(docid, metadata)
        

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
