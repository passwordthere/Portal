from pyVmomi import vim, vmodl

from .vcenter_managers import Manager


class OperatorBoy(Manager):
    def wait_for(self, task):
        task_done = False
        while not task_done:
            if task.info.state == 'success':
                print(task.info.result)
                return task.info.state
            if task.info.state == 'error':
                print(task.info.error)
                task_done = True

    def clone_vm(self, template_name, vm_name, dc_name, hv_name, vm_cpu, vm_memory):
        try:
            # 虚拟机位置
            dest_hv = self.get_obj(hv_name, [vim.HostSystem])
            dest_dc = self.get_obj(dc_name, [vim.Datacenter])
            dest_ds = dest_hv.datastore[0]
            dest_resource_pool = dest_hv.parent.resourcePool
            dest_folder = dest_dc.vmFolder
            relospec = vim.vm.RelocateSpec()
            relospec.datastore = dest_ds
            relospec.pool = dest_resource_pool
            # 虚拟机配置
            vm_conf = vim.vm.ConfigSpec()
            vm_conf.numCPUs = int(vm_cpu)
            vm_conf.memoryMB = 1024 * int(vm_memory)
            clonespec = vim.vm.CloneSpec()
            clonespec.location = relospec
            clonespec.powerOn = False
            template = self.get_vm(template_name)
            task = template.Clone(folder=dest_folder, name=vm_name, spec=clonespec)
            state = self.wait_for(task)
            if task.info.state == 'success':
                return True
        except Exception as e:
            print(e)
            print('克隆虚拟机：克隆时失败')
            print('-' * 70)

    def assign_ip(self, vm_name, vm_ip, vm_netmask, vm_gateway):
        try:
            # 虚拟机IP
            vm = self.get_obj(vm_name, [vim.VirtualMachine])
            adaptermap = vim.vm.customization.AdapterMapping()
            adaptermap.adapter = vim.vm.customization.IPSettings()
            adaptermap.adapter.ip = vim.vm.customization.FixedIp()
            adaptermap.adapter.ip.ipAddress = vm_ip
            adaptermap.adapter.subnetMask = vm_netmask
            gateway = vm_gateway
            adaptermap.adapter.gateway = gateway
            # 虚拟机DNS Important: 询问DNS是否分环境
            globalip = vim.vm.customization.GlobalIPSettings()
            globalip.dnsServerList = ['10.138.60.47', '10.138.61.47']
            # 虚拟机Hostname
            ident = vim.vm.customization.LinuxPrep()
            ident.hostName = vim.vm.customization.FixedName()
            ident.hostName.name = 'localhost'
            customspec = vim.vm.customization.Specification()
            customspec.nicSettingMap = [adaptermap]
            customspec.globalIPSettings = globalip
            customspec.identity = ident
            task = vm.Customize(spec=customspec)
            self.wait_for(task)
        except Exception as e:
            print(e)
            print('克隆虚拟机：设置网络时失败')
            print('-' * 70)

    # 加 硬盘
    def add_disk(self, vm_name, vm_disk_size, vm_disk_type):
        try:
            vm = self.get_obj(vm_name, [vim.VirtualMachine])
            spec = vim.vm.ConfigSpec()
            unit_number = 0
            controller = None
            for device in vm.config.hardware.device:
                if hasattr(device.backing, 'fileName'):
                    unit_number = int(device.unitNumber) + 1
                    # unit_number 7 reserved for scsi controller
                    if unit_number == 7:
                        unit_number += 1
                    if unit_number >= 16:
                        print("至多可加15块！")
                        return -1
                if isinstance(device, vim.vm.device.VirtualSCSIController):
                    controller = device
            if controller is None:
                print("磁头丢失！")
                return -1
            dev_changes = []
            new_disk_kb = int(vm_disk_size) * 1024 * 1024
            disk_spec = vim.vm.device.VirtualDeviceSpec()
            disk_spec.fileOperation = "create"
            disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
            disk_spec.device = vim.vm.device.VirtualDisk()
            disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
            if vm_disk_type:
                disk_spec.device.backing.thinProvisioned = True
            disk_spec.device.backing.diskMode = 'persistent'
            disk_spec.device.unitNumber = unit_number
            disk_spec.device.capacityInKB = new_disk_kb
            disk_spec.device.controllerKey = controller.key
            dev_changes.append(disk_spec)
            spec.deviceChange = dev_changes
            task = vm.ReconfigVM_Task(spec=spec)
            self.wait_for(task)
        except Exception as e:
            print(e)
            print('克隆虚拟机：添加硬盘时失败')
            print('-' * 70)

    def clone_flow(self, template_name, vm_name, dc_name, hv_name, vm_cpu, vm_memory,
                   vm_ip, vm_netmask, vm_gateway, vm_disk_size, vm_disk_type):
        task = self.clone_vm(template_name=template_name, vm_name=vm_name, dc_name=dc_name, hv_name=hv_name,
                             vm_cpu=vm_cpu, vm_memory=vm_memory)
        if task:
            self.assign_ip(vm_name=vm_name, vm_ip=vm_ip, vm_netmask=vm_netmask, vm_gateway=vm_gateway)
            self.add_disk(vm_name=vm_name, vm_disk_size=vm_disk_size, vm_disk_type=vm_disk_type)


class OperatorGirl(Manager):
    def collect_properties(self, obj_type, path_set, include_mors=True):
        collector = self.content.propertyCollector
        obj_spec = vmodl.query.PropertyCollector.ObjectSpec()
        obj_spec.obj = self.view_ref
        obj_spec.skip = True
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec()
        traversal_spec.name = 'traverseEntities'
        traversal_spec.path = 'view'
        traversal_spec.skip = False
        traversal_spec.type = self.view_ref.__class__
        obj_spec.selectSet = [traversal_spec]
        property_spec = vmodl.query.PropertyCollector.PropertySpec()
        property_spec.type = obj_type
        property_spec.pathSet = path_set
        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = [obj_spec]
        filter_spec.propSet = [property_spec]
        props = collector.RetrieveContents([filter_spec])
        data = []
        for obj in props:
            properties = {}
            for prop in obj.propSet:
                properties[prop.name] = prop.val
            if include_mors:
                properties['obj'] = obj.obj
            data.append(properties)
        return data

    def get_templates(self):
        template_folder = self.get_obj('系统模板', [vim.Folder])
        container = self.content.viewManager.CreateContainerView(template_folder, [vim.VirtualMachine], False)
        templates = []
        for managed_object_ref in container.view:
            templates.append(managed_object_ref)
        return templates
