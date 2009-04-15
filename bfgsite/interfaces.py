from zope.interface import Interface

class IWebSite(Interface):
    pass

class IBin(Interface):
    pass

class IPasteBin(Interface):
    pass

class ITutorialBin(Interface):
    pass

class IPasteEntry(Interface):
    pass

class ITutorial(Interface):
    pass

class IObjectModifiedEvent(Interface):
    pass

class ISearchText(Interface):
    pass

class IBatchInfo(Interface):
    pass
