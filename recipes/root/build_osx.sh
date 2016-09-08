#!/usr/bin/env bash

CXXFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" \
CFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" \
CPPFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" \
CLINGCXXFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" \
LD_LIBRARY_PATH="$PREFIX/lib" \
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=$PREFIX \
    -Dgnuinstall=ON \
    -Droofit=ON \
    -Dtesting=OFF \
    -Dcastor=OFF \
    -Dminuit2=ON \
    -Dbuiltin_ftgl=ON \
    -Dbuiltin_freetype=ON \
    -Dbuiltin_glew=ON \
    -Dbuiltin_pcre=ON \
    -Dbuiltin_zlib=ON \
    -Dbuiltin_lzma=ON \
    -Dbuiltin_xrootd=ON

CXXFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" \
CFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" \
CPPFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" \
CLINGCXXFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" \
LD_LIBRARY_PATH="$PREFIX/lib/" \
make -j$CPU_COUNT

make install

# Make symlinks to python's site-packages directory
SITE_PACKAGES_DIR=$(python -c "import site; print(site.getsitepackages()[0])")
ln -s $PREFIX/lib/root $SITE_PACKAGES_DIR/root
ln -s $PREFIX/lib/root/ROOT.py $SITE_PACKAGES_DIR/ROOT.py
ln -s $PREFIX/lib/root/ROOT.pyc $SITE_PACKAGES_DIR/ROOT.pyc
ln -s $PREFIX/lib/root/ROOT.pyo $SITE_PACKAGES_DIR/ROOT.pyo

# Modify ROOT.py to append to the path
sed -i 's/import os, sys, types/import os, sys, types\nsys.path.append(os.path.join(os.path.dirname(__file__), "root"))/g' $PREFIX/lib/root/ROOT.py

# Copy a script into the bin directory which can be used for fixing paths inside
# the various binary files
cp ${RECIPE_DIR}/fix-binary.py $PREFIX/share/root/fix-binary.py
cp ${RECIPE_DIR}/cleanup.py $PREFIX/share/root/cleanup.py
