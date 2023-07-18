from tnzapi.api.addressbook.contacts.requests.create import ContactCreate
from tnzapi.api.addressbook.contacts.requests.delete import ContactDelete
from tnzapi.api.addressbook.contacts.requests.detail import ContactDetail
from tnzapi.api.addressbook.contacts.requests.list import ContactList
from tnzapi.api.addressbook.contacts.requests.update import ContactUpdate

class Contact(object):
    
    def __init__(self):
        self._create = None
        self._update = None
        self._read = None
        self._delete = None
        self._list = None
        
    # Create

    def Create(self, **kwargs):

        if self._create != None:
            del(self._create)

        self._create = ContactCreate(kwargs)

        return self._create.Create().Data
    
    async def CreateAsync(self, **kwargs):
        
        if self._create != None:
            del(self._create)

        self._create = ContactCreate(kwargs)

        return await self._create.CreateAsync().Data
    
    # Update

    def Update(self, **kwargs):
        
        if self._update != None:
            del(self._update)

        self._update = ContactUpdate(kwargs)

        return self._update.Update().Data
    
    async def UpdateAsync(self, **kwargs):
        
        if self._update != None:
            del(self._update)

        self._update = ContactUpdate(kwargs)

        return await self._update.UpdateAsync().Data

    # Delete

    def Delete(self, **kwargs):
        
        if self._delete != None:
            del(self._delete)

        self._delete = ContactDelete(kwargs)

        return self._delete.Delete().Data
    
    async def DeleteAsync(self, **kwargs):
        
        if self._delete != None:
            del(self._delete)

        self._delete = ContactDelete(kwargs)

        return await self._delete.DeleteAsync().Data

    # Detail
    
    def Detail(self, **kwargs):
        
        if self._read != None:
            del(self._read)

        self._read = ContactDetail(kwargs)

        return self._read.Detail().Data
    
    async def DetailAsync(self, **kwargs):
        
        if self._read != None:
            del(self._read)

        self._read = ContactDetail(kwargs)

        return await self._read.DetailAsync().Data

    # List

    def List(self, **kwargs):
        
        if self._list != None:
            del(self._list)

        self._list = ContactList(kwargs)

        return self._list.List().Data
    
    async def ListAsync(self, **kwargs):
        
        if self._list != None:
            del(self._list)

        self._list = ContactList(kwargs)

        return await self._list.ListAsync().Data