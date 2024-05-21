# NiimPrintX
![](docs/assets/NiimPrintX.gif)
```shell
 brew install libffi
 brew install glib gobject-introspection cairo pango pkg-config
 
```

```shell
export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig"
export LDFLAGS="-L/usr/local/opt/libffi/lib"
export CFLAGS="-I/usr/local/opt/libffi/include"

```


```shell
poetry run pyinstaller --name NiimPrintX --paths $(poetry env info --path)/lib/python3.x/site-packages NiimPrintX/ui/__main__.py
poetry run pyinstaller --onefile --windowed --name NiimPrintX --paths $(poetry env info --path)/lib/python3.x/site-packages NiimPrintX/ui/__main__.py
poetry run pyinstaller NiimPrintX.spec
```