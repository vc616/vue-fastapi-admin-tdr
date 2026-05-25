import json

menus = [
    {'id': 17, 'name': '系统管理', 'path': '/system', 'menu_type': 'catalog', 'component': 'Layout', 'redirect': '/system/user', 'parent_id': 0},
    {'id': 18, 'name': '用户管理', 'path': 'user', 'menu_type': 'menu', 'component': '/system/user', 'redirect': None, 'parent_id': 17},
    {'id': 25, 'name': '设备管理', 'path': '/equipment', 'menu_type': 'catalog', 'component': 'Layout', 'redirect': '', 'parent_id': 0},
    {'id': 26, 'name': '鄄城取水泵站', 'path': 'juanchengpump', 'menu_type': 'catalog', 'component': 'Layout', 'redirect': '/equipment/juanchengpump/home', 'parent_id': 25},
    {'id': 27, 'name': '设备主页', 'path': 'home', 'menu_type': 'menu', 'component': '/equipment/juanchengpump', 'redirect': None, 'parent_id': 26},
    {'id': 28, 'name': '数据源配置', 'path': 'datasource-config', 'menu_type': 'menu', 'component': '/equipment/juanchengpump/datasource-config', 'redirect': None, 'parent_id': 26},
    {'id': 32, 'name': '120bar中试', 'path': '120bartest', 'menu_type': 'catalog', 'component': 'Layout', 'redirect': '/equipment/120bartest/home', 'parent_id': 25},
    {'id': 33, 'name': '设备主页', 'path': 'home', 'menu_type': 'menu', 'component': '/equipment/120bartest', 'redirect': '', 'parent_id': 32},
    {'id': 34, 'name': '数据源配置', 'path': 'datasource-config', 'menu_type': 'menu', 'component': '/equipment/120bartest/datasource-config', 'redirect': '', 'parent_id': 32},
]

menu_map = {m['id']: dict(m, children=[]) for m in menus}
roots = []
for m in menus:
    if m['parent_id'] == 0:
        roots.append(menu_map[m['id']])
    else:
        menu_map[m['parent_id']]['children'].append(menu_map[m['id']])

def buildRoutes(routes, parentPath=''):
    result = []
    for e in routes:
        isCatalog = e['menu_type'] == 'catalog'
        if e['path'].startswith('/'):
            fullPath = e['path']
        elif parentPath:
            fullPath = f'{parentPath}/{e["path"]}'
        else:
            fullPath = f'/{e["path"]}'
        
        route = {
            'name': e['name'],
            'path': e['path'],
            'fullPath': fullPath,
            'component': None if isCatalog else 'Layout',
            'isHidden': e.get('is_hidden', False),
            'redirect': e.get('redirect'),
            'isCatalog': isCatalog,
            'children': [],
        }
        
        if e['children'] and len(e['children']) > 0:
            route['children'] = buildRoutes(e['children'], fullPath)
        elif e['component'] and e['component'] != 'Layout':
            componentPath = f'/src/views{e["component"]}/index.vue'
            route['children'].append({
                'name': f'{e["name"]}Default',
                'path': '',
                'component': componentPath,
                'isHidden': True,
            })
        
        result.append(route)
    return result

def flattenNestedCatalogs(routes):
    result = []
    for route in routes:
        if route['isCatalog'] and route['component'] is None and route['children']:
            flatRoutes = extractFlatRoutes(route['children'], route['path'])
            result.extend(flatRoutes)
        else:
            result.append(route)
    return result

def extractFlatRoutes(children, parentPath):
    result = []
    for child in children:
        if child['isCatalog'] and child['component'] is None and child['children']:
            childPath = parentPath if parentPath else ''
            childPath = f'{childPath}/{child["path"]}'
            result.extend(extractFlatRoutes(child['children'], childPath))
        else:
            if parentPath:
                fullPath = child['path'].startswith('/') and child['path'] or f'{parentPath}/{child["path"]}'
            else:
                fullPath = child['path'].startswith('/') and child['path'] or f'/{child["path"]}'
            
            uniqueName = fullPath.replace('/', '_').lstrip('_')
            
            if child['children']:
                uniqueChildren = []
                for gc in child['children']:
                    childUniqueName = gc['path'] and f'{uniqueName}_{gc["path"].replace("/", "_")}' or f'{uniqueName}_default'
                    uniqueChildren.append({**gc, 'name': childUniqueName})
                result.append({**child, 'path': fullPath, 'name': uniqueName, 'children': uniqueChildren})
            else:
                result.append({**child, 'path': fullPath, 'name': uniqueName})
    return result

routes = buildRoutes(roots)
print('=== After buildRoutes ===')
for r in routes:
    print(f'{r["name"]} ({r["path"]}) comp={r["component"]}')
    for c in r.get('children', []):
        print(f'  -> {c["name"]} ({c["path"]}) comp={c.get("component")}')

flatRoutes = flattenNestedCatalogs(routes)
print('\n=== After flattenNestedCatalogs ===')
for r in flatRoutes:
    print(f'{r["name"]} ({r["path"]}) comp={r.get("component")}')
    for c in r.get('children', []):
        print(f'  -> {c["name"]} ({c["path"]}) comp={c.get("component")}')
