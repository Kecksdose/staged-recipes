#!/usr/bin/env python
import logging as log
import os
import sys

log.basicConfig(
    filename=os.path.join(os.environ['PREFIX'], '.messages.txt'),
    level=log.WARN
)


# TODO Automatically find this list
DEFAULT_FILES = [
    'bin/genreflex',
    'bin/proofd',
    'bin/root',
    'bin/rootcint',
    'bin/rootcling',
    'etc/root/allDict.cxx.pch',
    'lib/root/libASImage.so',
    'lib/root/libCling.so',
    'lib/root/libCore.so',
    'lib/root/libEG.so',
    'lib/root/libGeom.so',
    'lib/root/libGpad.so',
    'lib/root/libGraf.so',
    'lib/root/libGui.so',
    'lib/root/libGuiHtml.so',
    'lib/root/libGviz.so',
    'lib/root/libHtml.so',
    'lib/root/libNet.so',
    'lib/root/libPostscript.so',
    'lib/root/libProof.so',
    'lib/root/libProofBench.so',
    'lib/root/libPyROOT.so',
    'lib/root/libRGL.so',
    'lib/root/libRIO.so',
    'lib/root/libRSQLite.so',
    'lib/root/libRint.so',
    'lib/root/libRootAuth.so',
    'lib/root/libSessionViewer.so',
    'lib/root/libTreeViewer.so',
    'lib/root/libXMLParser.so',
    'lib/root/libXrdAppUtils.so.1.0.0',
    'lib/root/libXrdBwm-4.so',
    'lib/root/libXrdCksCalczcrc32-4.so',
    'lib/root/libXrdCl.so.2.0.0',
    'lib/root/libXrdClient.so.2.0.0',
    'lib/root/libXrdCrypto.so.1.0.0',
    'lib/root/libXrdCryptoLite.so.1.0.0',
    'lib/root/libXrdCryptossl-4.so',
    'lib/root/libXrdFfs.so.2.0.0',
    'lib/root/libXrdFileCache-4.so',
    'lib/root/libXrdHttp-4.so',
    'lib/root/libXrdOssSIgpfsT-4.so',
    'lib/root/libXrdPosix.so.2.0.0',
    'lib/root/libXrdPosixPreload.so.1.0.0',
    'lib/root/libXrdProofd.so',
    'lib/root/libXrdPss-4.so',
    'lib/root/libXrdSec-4.so',
    'lib/root/libXrdSecgsi-4.so',
    'lib/root/libXrdSecgsiAUTHZVO-4.so',
    'lib/root/libXrdSecgsiGMAPDN-4.so',
    'lib/root/libXrdSecgsiGMAPLDAP-4.so',
    'lib/root/libXrdSecpwd-4.so',
    'lib/root/libXrdSecsss-4.so',
    'lib/root/libXrdSecunix-4.so',
    'lib/root/libXrdServer.so.2.0.0',
    'lib/root/libXrdThrottle-4.so',
    'lib/root/libXrdUtils.so.2.0.0',
    'lib/root/libXrdXrootd-4.so'
]


def fix_file(filename, env_path, padded_env_path=None):
    """Modify `filename` to be correctly linked with the new enviroment.

    Iterate through `filename` replacing all instances `env_path` with
    `padded_env_path` while also removing an equivilent number of null bytes.
    If `padded_env_path` is `None` only output is printed and no changes are
    made to the file.

    Parameters
    ----------
    filename : string
        Relative path to the binary file that should be modified
    env_path : string
        The path to the conda enviroment
    padded_env_path : string
        The padded path that links to the conda enviroment

    TODO: This can proabably be optimised by using regex
    """
    filename = os.path.join(env_path, filename)

    if not os.path.isfile(filename):
        log.warn('Failed to find file, skipping: {0}'.format(filename))
        return

    log.info('Running for: {0}'.format(filename))

    env_path = env_path.encode('utf-8')
    if padded_env_path is not None:
        padded_env_path = padded_env_path.encode('utf-8')

    with open(filename, 'rb') as f:
        data = f.read()

    i = 0
    while env_path in data[i:]:
        i = data.index(env_path, i)
        l = data.index(b'\x00', i)+5
        match = bytes(data[i-30:i+l])
        log.debug('BEFORE: {0}'.format(format_match(match)))

        if padded_env_path is not None:
            env_path_suffix = match[
                30+len(env_path):
                match.index(b'\x00', 30)
            ]
            match = (
                match[:30] +
                padded_env_path +
                env_path_suffix +
                match[30+len(env_path_suffix)+len(padded_env_path):]
            )
            log.debug('AFTER:  {0}'.format(format_match(match)))

            data = data[:i-30] + match + data[i+l:]

            i += len(padded_env_path)
        else:
            i += len(env_path)

    if padded_env_path is not None:
        with open(filename, 'wb') as f:
            f.write(data)


def format_match(match):
    return repr(match[0:400]).replace('\\x00', '-')[0:100]


if __name__ == '__main__':
    if sys.platform == "linux" or sys.platform == "linux2":
        env_path = os.environ['PREFIX']

        if len(env_path) > 75:
            log.fatal("The conda enviroment's path ({0}) is too long for this "
                      "build of ROOT (max: 75 characters).".format(env_path))
            sys.exit(-1)

        padded_env_path = os.path.join(env_path, 'symlink_for_root'+'_pad'*100)
        padded_env_path = padded_env_path[:80]

        if os.path.exists(padded_env_path):
            log.fatal('Unable to create symlink: {0}'.format(padded_env_path))
            sys.exit(-1)

        os.symlink(env_path, padded_env_path)

        for fn in DEFAULT_FILES:
            fix_file(fn, env_path, padded_env_path)

        log.warn(
            'If when launching ROOT the following error message is seen:\n'
            '    > Fatal in <TROOT::InitInterpreter>: cannot load library '
            'libtinfo.so.5: cannot open shared object file: No such file or '
            'directory\n`ncurses` must be install using conda:\n'
            '    > conda install ncurses'
        )

    elif sys.platform == "darwin":
        pass
    elif sys.platform == "win32":
        pass
    else:
        log.fatal('Unrecognised platform: {0}'.format(sys.platform))
        sys.exit(-1)
