# simple-hw-info

A lightweight tool designed to retrieve basic hardware information for both Windows and Linux systems. Some information is retrieved using [fastfetch](https://github.com/fastfetch-cli/fastfetch), so you need to install it first.

Note: This package has not been extensively tested across all environments.

## Windows (powershell)

### Dependencies

```powershell
PS> winget install fastfetch # to recover: winget uninstall fastfetch
```

### Usage

Download `simple-hw-info.exe` from the [release page](https://github.com/aben20807/simple-hw-info/releases) and double-click it.

## Linux (bash)

### Dependencies

+ `>= Ubuntu 20.04`

    ```bash
    $ wget https://github.com/fastfetch-cli/fastfetch/releases/download/2.21.1/fastfetch-linux-amd64.deb
    $ sudo dpkg -i fastfetch-linux-amd64.deb # to recover: sudo apt-get remove fastfetch
    ```

+ `< Ubuntu 20.04`

    ```bash
    $ sudo apt install screenfetch
    ```

### Usage

```bash
$ curl -s https://raw.githubusercontent.com/aben20807/simple-hw-info/master/simple-hw-info/simple-hw-info.py | python3 # need to install curl
```

## Build the binary on Windows

```powershell
PS> pyinstaller -F -c --clean --exclude-module black,conda --icon=simple-hw-info.ico .\simple-hw-info\simple-hw-info.py
```

## Icon credit

The [icon (simple-hw-info.ico)](https://icon-icons.com/icon/info/65247) is from [EpicCoders](https://icon-icons.com/users/RMlIykMNITSXD96V7ULsv/icon-sets/) who shares it under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
