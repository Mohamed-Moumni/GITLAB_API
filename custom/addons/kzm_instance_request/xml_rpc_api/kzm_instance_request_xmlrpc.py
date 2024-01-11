import xmlrpc.client

class kzm_instance_request_API():
    def __init__(self, host, port, db, user, pwd):
        common = xmlrpc.client.ServerProxy(
            "http://%s:%d/xmlrpc/2/common" % (host, port))
        self.api = xmlrpc.client.ServerProxy(
            "http://%s:%d/xmlrpc/2/object" % (host, port))
        self.uid = common.authenticate(db, user, pwd, {})
        self.pwd = pwd
        self.db = db
        self.model = "kzm.instance.request"
    
    def _execute(self, method, arg_list, kwarg_dict=None):
        return self.api.execute_kw(self.db, self.uid, self.pwd, self.model,
                                   method, arg_list, kwarg_dict or {})
    
    
    def get_all_instances(self):
        instances_ids = self._execute("search",[[]])
        return self._execute("read", [instances_ids])
    
    def get_instances_by_state(self, state=None):
        if state == None:
            state = "Brouillon"
        domain = ['state', '=', state]
        instances_ids = self._execute("search", [[domain]])
        return self._execute("read", [instances_ids])
        
    
    def create_instance(self, cpu=None, url=None, disk=None, ram=None):
        instance = {
            'cpu':cpu,
            'url':url,
            'disk':disk,
            'ram':ram
        }
        return self._execute("create",[instance])

if __name__ == '__main__':
    host, port, db = "localhost", 8069, "odoo_db"
    user, pwd = "mohawatch101@gmail.com", "Moumni2006"
    API = kzm_instance_request_API(host, port,db, user,pwd)
    instances = API.get_instances_by_state("Soumise")
    print(instances)