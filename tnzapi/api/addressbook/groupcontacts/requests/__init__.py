

from tnzapi.api.addressbook.groupcontacts.requests.create import GroupContactCreate
from tnzapi.api.addressbook.groupcontacts.requests.delete import GroupContactDelete
from tnzapi.api.addressbook.groupcontacts.requests.detail import GroupContactDetail
from tnzapi.api.addressbook.groupcontacts.requests.list import GroupContactList


class GroupContact(object):
    
    def __init__(self):
        self._create = None
        self._read = None
        self._delete = None
        self._list = None
        
    # Create

    def Create(self, **kwargs):

        if self._create != None:
            del(self._create)

        self._create = GroupContactCreate(kwargs)

        return self._create.Create().Data
    
    async def CreateAsync(self, **kwargs):
        
        if self._create != None:
            del(self._create)

        self._create = GroupContactCreate(kwargs)

        return await self._create.CreateAsync().Data
    
    # Delete

    def Delete(self, **kwargs):
        
        if self._delete != None:
            del(self._delete)

        self._delete = GroupContactDelete(kwargs)

        return self._delete.Delete().Data
    
    async def DeleteAsync(self, **kwargs):
        
        if self._delete != None:
            del(self._delete)

        self._delete = GroupContactDelete(kwargs)

        return await self._delete.DeleteAsync().Data

    # Detail
    
    def Detail(self, **kwargs):
        
        if self._read != None:
            del(self._read)

        self._read = GroupContactDetail(kwargs)

        return self._read.Detail().Data
    
    async def DetailAsync(self, **kwargs):
        
        if self._read != None:
            del(self._read)

        self._read = GroupContactDetail(kwargs)

        return await self._read.DetailAsync().Data

    # List

    def List(self, **kwargs):
        
        if self._list != None:
            del(self._list)

        self._list = GroupContactList(kwargs)

        return self._list.List().Data
    
    async def ListAsync(self, **kwargs):
        
        if self._list != None:
            del(self._list)

        self._list = GroupContactList(kwargs)

        return await self._list.ListAsync().Data