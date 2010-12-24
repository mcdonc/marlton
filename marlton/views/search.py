from zope.index.text.parsetree import ParseError

from pyramid.traversal import find_model
from pyramid.view import view_config
from pyramid.url import resource_url

from marlton.catalog import find_catalog
from marlton.interfaces import IWebSite
from marlton.utils import API

@view_config(name='searchresults', for_=IWebSite, permission='view',
             renderer='marlton.views:templates/searchresults.pt')
def searchresults(context, request):
    catalog = find_catalog(context)

    text = request.params.get('text')
    batch_size = int(request.params.get('batch_size', 20))
    batch_start = int(request.params.get('batch_start', 0))
    sort_index = request.params.get('sort_index', None)
    reverse = bool(request.params.get('reverse', False))
    message = ''

    if text is not None:
        if text:
            try:
                numdocs, docids = catalog.search(sort_index=sort_index,
                                                 reverse=reverse,
                                                 text=text)
                docids = list(docids)
            except ParseError:
                numdocs, docids = 0, []
        else:
            numdocs, docids = 0, []
            message = 'Bad query'
    else:
            numdocs, docids = 0, []

    i = 0

    batch = []

    if numdocs > 0:
        for docid in docids:
            i += 1
            if i > batch_start+ batch_size:
                break
            if i < batch_start:
                continue
            path = catalog.document_map.address_for_docid(docid)
            md = dict(catalog.document_map.get_metadata(docid))
            if path.startswith('sphinx:'):
                scheme, rest = path.split(':', 1)
                if text.lower() in md['text'].lower():
                    firstpos = md['text'].lower().find(text.lower())
                else:
                    firstpos = 0
                start = firstpos -150
                if start < 0:
                    start = 0
                teaser = '%s ...' % md['text'][start:start+300]
                md['url'] = rest
                md['teaser'] = teaser
            else:
                model = find_model(context, path)
                url = resource_url(model, request)
                md['url'] = url
            batch.append(md)

    def _batchURL(query, batch_start=0):
        query['batch_start'] = batch_start
        return resource_url(context, request, request.view_name,
                            query=query)

    batch_info = {}

    previous_start = batch_start - batch_size

    if previous_start < 0:
        previous_batch_info = None
    else:
        previous_end = previous_start + batch_size
        if previous_end > numdocs:
            previous_end = numdocs
        size = previous_end - previous_start
        previous_batch_info = {}
        query = {'text':text, 'reverse':reverse, 'batch_size':batch_size}
        previous_batch_info['url'] = _batchURL(query, previous_start)
        previous_batch_info['name'] = (
            'Previous %s entries (%s - %s)' % (size, previous_start+1,
                                               previous_end))
    batch_info['previous_batch'] = previous_batch_info

    next_start = batch_start + batch_size
    if next_start >= numdocs:
        next_batch_info = None
    else:
        next_end = next_start + batch_size
        if next_end > numdocs:
            next_end = numdocs
        size = next_end - next_start
        next_batch_info = {}
        query = {'text':text, 'reverse':reverse, 'batch_size':batch_size}
        next_batch_info['url'] = _batchURL(query, next_start)
        next_batch_info['name'] = (
            'Next %s entries (%s - %s of %s)' % (size,
                                                 next_start+1,
                                                 next_end,
                                                 numdocs))
    batch_info['next_batch'] = next_batch_info
    batch_info['batching_required'] = next_batch_info or previous_batch_info

    return dict(
        api = API(context, request),
        batch = batch,
        batch_info = batch_info,
        numdocs = numdocs,
        message = message,
        )

