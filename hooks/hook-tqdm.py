from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('tqdm')
# from PyInstaller.utils.hooks import copy_metadata

# datas = copy_metadata('tqdm')
