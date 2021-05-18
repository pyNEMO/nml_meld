# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

'''
Created on Tue Oct 30 15:19:56 2018

Entry point for pynemo_nml

@author James Harle

$Last commit on:$
'''

import sys, getopt
from . import pynemo_nml

def main():
    """ Main function which checks the command line parameters and
        passes them to the main routine """

    gui = False

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hg", ["help","gui"])
    except getopt.GetoptError:
        print("usage: pynemo_nml [-g] <namelist1> <namelist2> ")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("usage: pynemo_nml [-g] <namelist1> <namelist2> ")
            print("       -g (optional) will open a GUI")
            sys.exit()
        elif opt in("-g", "--gui"):
            gui = True
    
    if len(args) < 2:
        print("usage: pynemo_nml [-g] <namelist1> <namelist2>")
        sys.exit(2)
    if len(args) > 2:
        print("usage: pynemo_nml [-g] <namelist1> <namelist2>")
        sys.exit(2)
    nlist_1, nlist_2 = args
    
    if nlist_1 == "":
        print("usage: pynemo_nml [-g] <namelist1> <namelist2>")
        sys.exit(2)
    elif nlist_2 == "":
        print("usage: pynemo_nml [-g] <namelist1> <namelist2>")
        sys.exit(2)

    pynemo_nml.compare(nlist_1, nlist_2, gui)

    
if __name__ == "__main__":
    main()
