import time

from zope.interface import providedBy
from zope.component import queryAdapter
from zope.interface.declarations import Declaration

from pyramid.traversal import model_path
from pyramid.traversal import find_interface

from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.keyword import CatalogKeywordIndex
from repoze.catalog.indexes.text import CatalogTextIndex
from repoze.catalog.indexes.path import CatalogPathIndex
from repoze.catalog.document import DocumentMap

from marlton.interfaces import IWebSite
from marlton.interfaces import ISearchText

def get_search_text(object, default):
    adapter = queryAdapter(object, ISearchText)
    if adapter is None:
        return default
    return adapter()

def get_creator(object, default):
    return getattr(object, 'creator', default)

def _get_date(object, default, name):
    date = getattr(object, 'modified', None)
    if date is None:
        return default
    # we can't store datetimes directly in the catalog because they
    # can't be compared with anything
    timetime = time.mktime(date.timetuple())
    # creation "minute" actually to prevent too-granular storage
    date = int(str(int(timetime))[:-2])
    return date

def get_modified_date(object, default):
    return _get_date(object, default, 'modified')

def get_created_date(object, default):
    return _get_date(object, default, 'created')

def get_path(object, default):
    if not hasattr(object, '__name__'):
        return default
    return model_path(object)

def get_interfaces(object, default):
    # we unwind all derived and immediate interfaces using spec.flattened()
    # (providedBy would just give us the immediate interfaces)
    provided_by = list(providedBy(object))
    spec = Declaration(provided_by)
    ifaces = list(spec.flattened())
    return ifaces

def populate_catalog(site):
    catalog = site.catalog = Catalog()
    catalog['text'] = CatalogTextIndex(get_search_text)
    catalog['interfaces'] = CatalogKeywordIndex(get_interfaces)
    catalog['creator'] = CatalogFieldIndex(get_creator)
    catalog['modified'] = CatalogFieldIndex(get_modified_date)
    catalog['created'] = CatalogFieldIndex(get_modified_date)
    catalog['path'] = CatalogPathIndex(get_path)
    catalog.document_map = DocumentMap()

def find_catalog(context):
    return find_interface(context, IWebSite).catalog

