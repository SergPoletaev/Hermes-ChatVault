from pathlib import Path
import importlib.util
import unittest
import json
import hashlib
import re
ROOT=Path(__file__).resolve().parents[1]
class TestPublicPackage(unittest.TestCase):
    def test_root_desktop_plugin(self):
        self.assertEqual((ROOT/'plugin.js').read_bytes(), (ROOT/'desktop/plugin.js').read_bytes())
        self.assertIn("const PLUGIN_ID = 'hermes-chat-vault'",(ROOT/'plugin.js').read_text('utf-8'))
    def test_desktop_only(self):
        self.assertFalse((ROOT/'plugin.yaml').exists())
    def test_hidden_gitignore(self):
        self.assertTrue((ROOT/'.gitignore').is_file(), 'GitHub must include hidden .gitignore')

    def test_powershell_does_not_assign_readonly_home(self):
        import re
        for name in ('Install.ps1', 'Uninstall.ps1'):
            script=(ROOT/name).read_text('utf-8-sig')
            self.assertNotRegex(script, r'(?im)\$home\s*=', name + ': PowerShell $HOME is read-only')

    def test_release_version_and_compiled_checksum(self):
        manifest = json.loads((ROOT/'BUILD-MANIFEST.json').read_text('utf-8'))
        version = manifest['version']
        compiled = (ROOT/'plugin.js').read_bytes()
        self.assertEqual(hashlib.sha256(compiled).hexdigest(), manifest['compiled_sha256'])
        plugin = compiled.decode('utf-8')
        self.assertIn(f"const PLUGIN_VERSION = '{version}-vault'", plugin)
        self.assertIn(f"VERSION = '{version}'", (ROOT/'scripts/build.py').read_text('utf-8'))
        self.assertIn(f"0.1.0 -> {version}", (ROOT/'scripts/upgrade_v02.py').read_text('utf-8'))
        for name in ('Install.ps1', 'Install.sh', 'README.md', 'docs/ARCHITECTURE.md'):
            self.assertIn(version, (ROOT/name).read_text('utf-8-sig'), name)

    def test_release_documentation(self):
        readme = (ROOT/'README.md').read_text('utf-8')
        changelog = (ROOT/'CHANGELOG.md').read_text('utf-8')
        version = json.loads((ROOT/'BUILD-MANIFEST.json').read_text('utf-8'))['version']
        self.assertEqual(len(re.findall(r'(?m)^## '+re.escape(version)+r'\b', changelog)), 1)
        self.assertRegex(changelog, r'(?m)^## 0\.2\.1\b')
        for stale in ('Until you publish the GitHub repository', '发布 GitHub 仓库之前',
                      'जब तक GitHub पर रिपॉज़िटरी प्रकाशित नहीं होती'):
            self.assertNotIn(stale, readme)
        self.assertIn(f'Версия {version}', readme)
        self.assertIn('https://github.com/smallmj/hermes-chat-share', readme)

    def test_privacy_manifest(self):
        m=(ROOT/'BUILD-MANIFEST.json').read_text('utf-8')
        self.assertNotIn('original_sha256', m)
        self.assertIn('0.2.2',m)
if __name__=='__main__':unittest.main()
