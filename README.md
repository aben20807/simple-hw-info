# simple-hw-info

## Windows

### Dependencies

```powershell
$ winget install fastfetch # to recover: winget uninstall fastfetch
```

```powershell
$ pyinstaller -F -c --clean --exclude-module black,conda --icon=simple-hw-info.ico .\simple-hw-info\simple-hw-info.py
```

## Linux

### Dependencies

```bash
$ wget https://github.com/fastfetch-cli/fastfetch/releases/download/2.21.1/fastfetch-linux-amd64.deb # >= Ubuntu 20.04
$ sudo dpkg -i fastfetch-linux-amd64.deb # to recover: sudo apt-get remove fastfetch
```

```bash
$ sudo apt install screenfetch # < Ubuntu 20.04
```

## Icon credit

The [icon (simple-hw-info.ico)](https://icon-icons.com/icon/info/65247) is from [EpicCoders](https://icon-icons.com/users/RMlIykMNITSXD96V7ULsv/icon-sets/) who shares it under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
