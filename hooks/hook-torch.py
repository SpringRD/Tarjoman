# from PyInstaller.utils.hooks import get_package_paths

# datas = [(get_package_paths('torch')[1], "torch"),]
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('torch')
# from PyInstaller.utils.hooks import copy_metadata

# datas = copy_metadata('torch')
