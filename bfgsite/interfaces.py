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

class INavigation(Interface):
    def items(self):
        """ Return a navigation items dict """
