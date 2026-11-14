from pathlib import Path
import importlib.util
import unittest
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

    def test_privacy_manifest(self):
        m=(ROOT/'BUILD-MANIFEST.json').read_text('utf-8')
        self.assertNotIn('original_sha256', m)
        self.assertIn('0.2.2',m)
if __name__=='__main__':unittest.main()
