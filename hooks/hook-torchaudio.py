# from PyInstaller.utils.hooks import copy_metadata

# datas = copy_metadata('torchaudio')
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('torchaudio')
