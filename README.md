
```shell
 brew install libffi
 brew install glib gobject-introspection cairo pango pkg-config
 
```

```shell
export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig"
export LDFLAGS="-L/usr/local/opt/libffi/lib"
export CFLAGS="-I/usr/local/opt/libffi/include"

```