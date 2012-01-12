import atexit
import os
import subprocess
import ConfigParser
import logging

logger = logging.getLogger('SConsDebug')


def bf_to_str(bf):
    """Convert an element of GetBuildFailures() to a string
    in a useful way."""
    import SCons.Errors
    if bf is None: # unknown targets product None in list
        return '(unknown tgt)'
    elif isinstance(bf, SCons.Errors.StopError):
        return str(bf)
    elif bf.node:
        return str(bf.node) + ': ' + bf.errstr
    elif bf.filename:
        return bf.filename + ': ' + bf.errstr
    return 'unknown failure: ' + bf.errstr

def build_status():
    """Convert the build status to a 2-tuple, (status, msg)."""
    from SCons.Script import GetBuildFailures
    bf = GetBuildFailures()
    if bf:
        # bf is normally a list of build failures; if an element is None,
        # it's because of a target that scons doesn't know anything about.
        status = 'failed'
        failures_message = os.linesep.join(["Failed building %s" % bf_to_str(x)
                                      for x in bf if x is not None])
    else:
        # if bf is None, the build completed successfully.
        status = 'ok'
        failures_message = ''
    return (status, failures_message)

def display_build_status():
    """Display the build status.  Called by atexit.
    Here you could do all kinds of complicated things."""
    status, failures_message = build_status()
    if status == 'failed':
        print "FAILED!!!!"  # could display alert, ring bell, etc.
    elif status == 'ok':
        print "Build succeeded."
    print failures_message

atexit.register(display_build_status)



def echospawn( sh, escape, cmd, args, env ):
    """
    Spawn which echos stdout/stderr from the child.
    SCons uses its env['SPAWN'] variable every time it runs something,
    so this hooks it.
    From http://www.scons.org/wiki/BuildLog.
    """    
    # convert env from unicode strings
    asciienv = {}
    for key, value in env.iteritems():
        asciienv[key] = str(value)
   
    p = subprocess.Popen(
           args,
           env=asciienv,
           stderr=subprocess.PIPE,
           stdout=subprocess.PIPE,
           shell=True,
           universal_newlines=True)
    (stdout, stderr) = p.communicate()
   
    # Does this screw up the relative order of the two?
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)
    return p.returncode
 

