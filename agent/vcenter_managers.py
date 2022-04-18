import atexit
import time

from pyvim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim


class Manager:
    def __init__(self, service=0):
        self.service = service
        self.content = self.service.RetrieveContent()
        self.root_folder = self.content.rootFolder

        self.dc = self.get_objs([vim.Datacenter])
        self.ds = self.get_objs([vim.Datastore])
        self.hv = self.get_objs([vim.HostSystem])
        self.vm = self.get_objs([vim.VirtualMachine])
        self.view_ref = None

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, vc_ip):
        self._service = SmartConnectNoSSL(host=vc_ip, user='ace.com\\xucheng', pwd='XC_pwd@2022', port=443)
        atexit.register(Disconnect, self.service)

    def get_obj(self, obj_name, obj_type, recurse=True):
        obj = None
        container = self.content.viewManager.CreateContainerView(self.root_folder, obj_type, recurse)
        for managed_object_ref in container.view:
            if managed_object_ref.name == obj_name:
                obj = managed_object_ref
                break
        container.Destroy()
        if not obj:
            raise RuntimeError(obj_name + "对象不存在")
        return obj

    def get_objs(self, obj_type):
        obj_view = self.content.viewManager.CreateContainerView(self.root_folder, obj_type, True)
        objs = []
        for obj in obj_view.view:
            objs.append(obj)
        obj_view.Destroy()
        return objs

    @property
    def view_ref(self):
        return self._view_ref

    @view_ref.setter
    def view_ref(self, obj_type):
        container = self.content.rootFolder
        self._view_ref = self.content.viewManager.CreateContainerView(container=container, recursive=True)
