# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['src\\multi_stat_analysis\\__main__.py'],
             pathex=['src\\multi_stat_analysis'],
             binaries=[],
             datas=[('C:/workspace/Multiscale-Statistical-Analysis/resources/*', 'resources')],
             hiddenimports=['scipy.special.cython_special',
							 'pkg_resources.py2_warn',
							 'pyimod03_importers',
							 'pyi_rth_pkgres'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
			 
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
			 
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='MultiscaleStatisticalAnalysis',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
