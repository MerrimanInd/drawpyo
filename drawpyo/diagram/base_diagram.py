from ..xml_base import XMLBase

__all__ = ['DiagramBase']


class DiagramBase(XMLBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = kwargs.get("page", None)
        self.parent = kwargs.get("parent", None)

    # Parent property
    @property
    def parent_id(self):
        if self.parent is not None:
            return self.parent.id
        else:
            return 1


    # Parent object linking
    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, p):
        if p is not None:
            p.add_object(self)
            self._parent = p
        else:
            self._parent = None

    @parent.deleter
    def parent(self):
        self._parent.remove_object(self)
        self._parent = None



    # Page property
    @property
    def page_id(self):
        if self.page is not None:
            return self.page.id
        else:
            return 1

    # page object linking
    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, p):
        if p is not None:
            p.add_object(self)
            self._page = p
        else:
            self._page = None

    @page.deleter
    def page(self):
        self._page.remove_object(self)
        self._page = None
