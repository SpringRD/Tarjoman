# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['D:\\source\\Tarjoman\\main.py'],
             pathex=['C:\\Users\\net\\PycharmProjects\\translate\\venv\\Scripts'],
             binaries=[],
             datas=[('D:\\source\\Tarjoman\\resources_rc.py', '.'), ('D:\\source\\Tarjoman\\ui\\*.*', 'ui')],
             hiddenimports=['torchaudio', 'torchvision'],
             hookspath=['D:\\source\\Tarjoman\\hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
for d in a.datas:
	if '_C.cp36-win_amd64.pyd' in d[0]:
		a.datas.remove(d)
		break
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ترجمان',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='D:\\source\\Tarjoman\\resources\\images\\my_icon.ico')
