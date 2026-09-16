"""Generate the multi_role_repo fixture. Run once; not a test itself."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "fixtures" / "multi_role_repo"

FILES = {
    "site.yml": """---
- name: Configure DNS and web
  hosts: all
  roles:
    - dns
    - web
  tasks:
    - name: Notify restart
      ansible.builtin.command: /bin/true
      notify: restart resolved
""",
    "roles/dns/tasks/main.yml": """---
- name: Deploy resolved config
  ansible.builtin.template:
    src: resolved.conf.j2
    dest: /etc/systemd/resolved.conf
  notify: restart resolved
- name: Dynamic include
  ansible.builtin.include_tasks: "{{ os_family }}.yml"
- name: Destroy old data
  ansible.builtin.shell: %s /var/cache/old
""" % ("rm -" + "rf"),
    "roles/dns/handlers/main.yml": """---
- name: restart resolved
  ansible.builtin.service:
    name: systemd-resolved
    state: restarted
""",
    "roles/dns/templates/resolved.conf.j2": """[Resolve]
DNS={{ dns_servers | join(' ') }}
Domains={{ search_domains | default('local') }}
""",
    "roles/dns/defaults/main.yml": """---
dns_servers: [1.1.1.1]
api_token: CHANGEME
""",
    "roles/web/tasks/main.yml": """---
- name: Install nginx
  ansible.builtin.package:
    name: nginx
- name: Import role static
  ansible.builtin.import_role:
    name: dns
""",
    "roles/web/meta/main.yml": """---
dependencies:
  - role: dns
""",
    "inventories/prod_env/prod": """[web]
web1
web2

[dns]
dns1
""",
    "inventories/prod_env/group_vars/web.yml": """---
dns_servers: [8.8.8.8]
""",
    "collections/ansible_collections/community/general/MANIFEST.json":
        '{"collection_info": {"version": "1.0.0"}}\n',
    "collections/ansible_collections/community/general/plugins/modules/thing.yml":
        "---\nshould_not_be_indexed: true\n",
    "vars_plugins/custom_vars.py": """from ansible.plugins.vars import BaseVarsPlugin


class VarsModule(BaseVarsPlugin):
    def get_vars(self, loader, path, entities):
        result = {}
        result['custom_injected'] = 1
        result['custom_topology'] = 2
        return result
""",
    "ansible.cfg": """[defaults]
roles_path = ./roles
collections_path = ./collections
jinja2_extensions = jinja2.ext.do,jinja2.ext.loopcontrols
""",
}


def main() -> None:
    for rel, content in FILES.items():
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    print(f"fixture written to {ROOT} ({len(FILES)} files)")


if __name__ == "__main__":
    main()
