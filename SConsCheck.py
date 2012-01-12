import os
import sys
import subprocess
import distutils.sysconfig
import logging
from SConsVars import cfg
import SCons.Script


logger=logging.getLogger('SconsRoot')



def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath and is_exe(program):
        return program

    else:
        for path in os.environ['PATH'].split(os.pathsep):
            exe_file = os.path.join(path,program)
            if is_exe(exe_file):
                return exe_file
    return None


def latest_gcc(env):
    for version in ['4.7', '4.6', '4.5', '4.4']:
        for mp in ['', 'mp-']:
           cxx='g++-%s%s' % (mp,version)
           cc='gcc-%s%s' % (mp,version)
           wcxx=which(cxx)
           wcc=which(cc)
           if wcxx and wcc:
               env['CXX']=wcxx
               env['CC']=wcc
               env['CCVERSION']=version
               env['CXXVERSION']=version
               logger.debug('Found %s' % wcxx)
               return

    logger.error('Could not find g++ with a version.')
    return


cpp11_test = '''
#include <vector>
int main(int argc, char* argv[]) {
  std::vector<std::vector<int>> blah;
  auto dp = new std::vector<double>();
  dp->push_back(3.14);
  return 0;
}
'''

def CheckCPP11():
    '''
    This function generates a callable object (another function).
    '''
    def SimpleCall(context):
        context.Message('Checking for c++0x conformance...')
        result = context.TryLink(cpp11_test,'.cxx')
        if not result:
           for flag in ['-std=c++11','-std=c++0x']:
               context.Message('%s?...' % flag)
               context.env.AppendUnique(CXXFLAGS=[flag])
               result = context.TryCompile(cpp11_test,'.cxx')
               if result: break
               context.env['CXXFLAGS'].remove(flag)
        context.Result(result)
        return result
    return SimpleCall




class CheckSnippet:
    '''
    This just tries to compile and link a snippet of code.
    '''
    def __init__(self,name,snippet):
        self.snippet=snippet
        self.name=name
        
    def __call__(self,context):
        context.Message('Checking snippet %s...' % (self.name,))
        result = context.TryLink(self.snippet,'.cxx')
        context.Result(result)
        return result




class GenerateLibCheck:
    '''
    This generates an SCons check routine that will search
    hdirs and ldirs for the headers and libraries specified and
    add to the includes and libs the correct paths found.
    '''
    def __init__(self,name,headers,libs,hdirs,ldirs,lang='C++'):
        '''
        name is the name of the library.
        headers is a list of header files as you would put in includes.
        libs is a list of [library,symbol] pairs, where symbol may be None.
        hdirs are header directories.
        ldirs are library directories.
        '''
        self.name=name
        self.headers=headers
        self.libs=libs
        self.hdirs=hdirs
        self.ldirs=ldirs
        self.lang=lang
        
        # If the command line specifies a directory, then use just that.
        name=name.lower()
        SCons.Script.AddOption('--%s-inc' % name, dest='%s_inc' % name, type='string', nargs=1,
              action='store', metavar='DIR', help='Include directory for %s.' % name)
        SCons.Script.AddOption('--%s-lib' % name, dest='%s_lib' % name, type='string', nargs=1,
              action='store', metavar='DIR', help='Library directory for %s.' % name)
        hdir=SCons.Script.GetOption('%s_inc' % name)
        ldir=SCons.Script.GetOption('%s_lib' % name)
        if hdir:
            logger.debug('Using %s-inc from command line: %s' % (name,hdir))
            self.hdirs=[hdir]
        if ldir:
            logger.debug('Using %s-lib from command line: %s' % (name,ldir))
            self.ldirs=[ldir]


    def __call__(self,context):
        context.Message('Checking for %s...' % self.name)
        
        result = self.find_header(context)
        if result:
            result = self.find_libs(context)
            context.Result(result)
        return result


    def find_header(self,context):
        # Allow no headers listed.
        if not self.headers: return True
        result = context.sconf.CheckCXXHeader(self.headers)
        if result: return result
        for incdir in [d for d in self.hdirs if d not in context.env['CPPPATH']]:
            logger.debug('Looking in %s' % incdir)
            context.env.AppendUnique(CPPPATH=[incdir])
            result = context.sconf.CheckCXXHeader(self.headers)
            if result:
                context.Message('Found %s in %s' % (str(self.headers),incdir))
                break
            context.env['CPPPATH'].remove(incdir)
        return result
        

    def find_libs(self,context):
        if not self.libs: return 1
        result=1
        for lib_symbol in self.libs:
            res=self.find_lib(context,lib_symbol)
            if not res:
                result=res
        return result


    def find_lib(self,context,lib_symbol):
        if type(lib_symbol) is list:
            [lib,sym]=lib_symbol
        else:
            lib = lib_symbol
            sym = None
        context.env.AppendUnique(LIBS=[lib])

        result = context.sconf.CheckLib(lib,sym,None,self.lang,0)
        if result: return result

        for ldir in [d for d in self.ldirs if d not in context.env['LIBPATH']]:
            context.env.AppendUnique(LIBPATH=[ldir])
            context.Message('Is %s in %s?\n' % (lib,ldir))
            result = context.sconf.CheckLib(lib,sym,None,self.lang,0)
            if result: break
            context.env['LIBPATH'].remove(ldir)
 
        if not result:
            logger.error('Could not find %s library' % str(lib))
            context.env['LIBS'].remove(lib)
        return result


def CheckBoost(boost_libs):
    boost_hdirs=cfg.get_dir('Boost','hdirs')+cfg.get_dir('General','system_hdirs')
    boost_ldirs=cfg.get_dir('Boost','ldirs')+cfg.get_dir('General','system_ldirs')
    return GenerateLibCheck('Boost',['boost/mpl/list.hpp','boost/chrono.hpp'],
                        boost_libs,boost_hdirs,boost_ldirs)


def CheckBoostPython():
    boost_hdirs=cfg.get_dir('Boost','hdirs')+cfg.get_dir('General','system_hdirs')
    boost_ldirs=cfg.get_dir('Boost','ldirs')+cfg.get_dir('General','system_ldirs')
    return GenerateLibCheck('BoostPython',['boost/python.hpp'],
                        [['boost_python',None]],boost_hdirs,boost_ldirs)

def CheckPython():
    python_hdirs=cfg.get_dir('Python','hdirs')+cfg.get_dir('General','system_hdirs')
    python_ldirs=cfg.get_dir('Python','ldirs')+cfg.get_dir('General','system_ldirs')
    python_libs=cfg.get_lib('Python','libraries')
    python_hdirs.extend([distutils.sysconfig.get_python_inc()])
    return GenerateLibCheck('Python',['pyconfig.h'],
            python_libs,python_hdirs,python_ldirs)




def CheckNumpy():
    # Numpy sometimes has headers in /usr/include, but they can be under site-packages
    # or even in an Extras directory on some distributions. Ask numpy where it is.
    # Don't assume the python running scons is the same as what we want for the build.
    python_hdirs=cfg.get_dir('Python','hdirs')+cfg.get_dir('General','system_hdirs')
    python_ldirs=cfg.get_dir('Python','ldirs')+cfg.get_dir('General','system_ldirs')
    np_str='import os.path,numpy;print os.path.join(os.path.split(numpy.__file__)[0],"core","include")'
    np_inc=subprocess.check_output([cfg.get('Python','exe'),'-c',np_str]).strip()
    if not os.path.exists(np_inc):
        logger.error('The Python numpy header directory doesn\'t exist.')
    else:
        python_hdirs.append(np_inc)
    logger.debug('Looking for numpy include numpy/arrayobject.h in %s' % np_inc)
    return GenerateLibCheck('numpy',['pyconfig.h','Python.h','numpy/arrayobject.h'],
            None,python_hdirs,python_ldirs)
            
            
            
            
def CheckGeoTIFF():
    geotiff_hdirs=cfg.get_dir('geotiff','hdirs')+cfg.get_dir('General','system_hdirs')
    geotiff_ldirs=cfg.get_dir('geotiff','ldirs')+cfg.get_dir('General','system_ldirs')
    geotiff_hdirs = geotiff_hdirs+[os.path.join(x,'geotiff') for x in geotiff_hdirs]
    geotiff_libs=cfg.get_lib('geotiff','libraries')
    return GenerateLibCheck('Geotiff',['xtiffio.h'], geotiff_libs,
                        geotiff_hdirs,geotiff_ldirs,'C++')



def CheckTBB():
    '''
    Intel Threading Building Blocks
    '''
    tbb_hdirs=cfg.get_dir('tbb','hdirs')+cfg.get_dir('General','system_hdirs')
    tbb_ldirs=cfg.get_dir('tbb','ldirs')+cfg.get_dir('General','system_ldirs')
    tbb_libs=['tbb'] #cfg.get_lib('tbb','libraries').strip().split()
    return GenerateLibCheck('TBB',['tbb/parallel_for.h'],tbb_libs,
                            tbb_hdirs,tbb_ldirs,'C++')

