'''
This builds the raster_measure library. It's an SCons configuration file.

Build: "scons"
Targets:
  - cpp, builds all the pure C++ (Default)
  - wrapper, builds the Python wrapper dll
  - tiff_test, cluster_test are two test cases.
Clean: "scons -c"
Reset cache: "rm -rf .scon*"
Debug: "scons --echo"

There is a configuration file called default.cfg. If you want to change
values for a particular OS, like "linux2" or "darwin", then edit
linux2.cfg or darwin.cfg. If you have defaults just for your machine,
then create local.cfg and put those defaults there.

Want to know which of the variables in the cfg files were read? Look
at used.cfg after the build is done.
'''

import os
import sys
import subprocess
import distutils.sysconfig
import SConsDebug
import SConsCheck
from SConsVars import cfg
import logging


logger=logging.getLogger('SconsRoot')
logging.basicConfig(level=logging.DEBUG)

# The goals of the build decide what we find and include.
# 1. Command line determines what targets we need.
# 2. Targets have requirements.
# 3. Availability can determine optional things to include (like tcmalloc).

# Set preferred directories here. There is a hierarchy of what gets chosen.
# 1. Set from command line
# 2. Set from environment variable.
# 3. Set for this particular machine in some config file.
# 4. Set for this architecture.
# 5. Set as common default, such as /usr/include.


# Command-line Options that are arguments to SCons.
try:
    file_cpu=int(cfg.get('General','num_jobs'))
except:
    file_cpu=1
num_cpu=int(os.environ.get('NUM_CPU',file_cpu))
SetOption('num_jobs', num_cpu)
logger.info('running with -j %d' % int(GetOption('num_jobs')))

AddOption('--echo', dest='echo', action='store_true',default=False,
          help='This echoes what scons runs as tests in order to debug failed builds.')

env=Environment()

if GetOption('echo'):
    env['SPAWN']=SConsDebug.echospawn

cpp_compiler=cfg.get('General','cpp_compiler')
c_compiler=cfg.get('General','c_compiler')
if not (cpp_compiler and c_compiler):
    SConsCheck.latest_gcc(env)
if cpp_compiler:
    env['CXX']=cpp_compiler
if c_compiler:
    env['CC']=cpp_compiler


def DisallowSubst():
    #AllowSubstExceptions()
    # Cannot use AllowSubstExceptions without defining these variables
    # which the default tool leaves undefined.
    env.SetDefault(CPPFLAGS=[])
    env.SetDefault(CPPDEFINES=[])
    env.SetDefault(CXXCOMSTR='')
    env.SetDefault(RPATH=[])
    env.SetDefault(LIBPATH=[])
    env.SetDefault(LIBS=[])
    env.SetDefault(LINKCOMSTR='')
    env.SetDefault(SHCXXCOMSTR='')
    env.SetDefault(SHLINKCOMSTR='')



DisallowSubst()

env.AppendUnique(CCFLAGS=['-fPIC'])
env.AppendUnique(LINKFLAGS=['-fPIC'])
env.AppendUnique(CPPPATH=['.'])
optimization=cfg.get('General','optimization').strip().split()
if optimization:
    env.AppendUnique(CCFLAGS = optimization )


# These are tests of c++11 features, as listed by Wikipedia.
tests=dict()
cpp_tests=dict()

# Test for Rvalues?

cpp_tests['generalized_constant']= '''
#include <vector>
int main(int argc, char* argv[]) {
    constexpr int get_five() { return 5;}
    int some_value[get_five()+7];
  return 0;
}
'''


# Testing for extern template???


cpp_tests['initializer lists']= '''
#include <vector>
struct Object
{
    float first;
    int second;
};
int main(int argc, char* argv[]) {
    Object working;
    working.first=0.45f; working.second=7;
    Object scalar = { 0.43f, 10 };
    Object blah[] {{ 1.0f, 10 },{43.2f,29}};
  return 0;
}
'''

cpp_tests['uniform initialization']= '''
struct BasicStruct { int x; double y; };
struct AltStruct {
    AltStruct(int x, double y) : x_{x}, y_{y} {}
private:
    int x_; double y_;
};
int main(int argc, char* argv[]) {
    BasicStruct var1{5,3.2};
    AltStruct var2{2,4.3};
  return 0;
}
'''


cpp_tests['type inference auto']= '''
int main(int argc, char* argv[]) {
    auto variable = 5;
  return 0;
}
'''

cpp_tests['type inference decltype']= '''
int main(int argc, char* argv[]) {
    int some_int;
    decltype(some_int) other_int = 5;
  return 0;
}
'''


cpp_tests['range-based for-loop']= '''
int main(int argc, char* argv[]) {
    int my_array[5] = {1,2,3,4,5};
    for (int&x : my_array) {
      x *= 2;
}
  return 0;
}
'''

cpp_tests['lambda functions']= '''
#include <algorithm>
int main(int argc, char* argv[]) {
    int my_array[5] = {1,2,3,4,5};
    std::for_each(my_array,my_array+5,
    [](int var) { return 2*var; });
  return 0;
}
'''


cpp_tests['alternative function syntax']= '''
template<class Lhs, class Rhs>
  auto adding_func(const Lhs &lhs, const Rhs &rhs) -> decltype(lhs+rhs) {return lhs + rhs;}
struct SomeStruct  {
    auto func_name(int x, int y) -> int;
};
 
auto SomeStruct::func_name(int x, int y) -> int {
    return x + y;
}
int main(int argc, char* argv[]) {
    double res = adding_func(3.0,4.7);
    SomeStruct s;
    double other = s.func_name(3.7,4.2);
  return 0;
}
'''


cpp_tests['object construction constructors calling constructors']= '''
class SomeType {
    int number;
public:
    SomeType(int new_number) : number(new_number) {}
    SomeType() : SomeType(42) {}
};
int main(int argc, char* argv[]) {
    SomeType bare;
    SomeType with_argument(37);
  return 0;
}
'''


cpp_tests['object construction improvement using base constructor']= '''
class BaseClass {
    int val_;
public:
    BaseClass(int value) : val_(value) {}
};
 
class DerivedClass : public BaseClass {
public:
    using BaseClass::BaseClass;
};
int main(int argc, char* argv[]) {
    DerivedClass d(3);
  return 0;
}
'''


cpp_tests['explicit override']= '''
struct Base {
    float val_;
    virtual void some_func(float val) { val_=val* 2; }
};
 
struct Derived : Base {
    virtual void some_func(float val) override { val_=val * 4; }
};
int main(int argc, char* argv[]) {
    Derived d;
    d.some_func(3);
  return 0;
}
'''

cpp_tests['explicit final']= '''
struct Base2 {
    int blah_;
    virtual void f() final {blah_=7;};
};
struct Base3 : public Base2 {
    virtual void g() { blah_=3;}
};
int main(int argc, char* argv[]) {
  return 0;
}
'''


cpp_tests['nullptr']= '''
void foo(char* howdy) { if (howdy) howdy[0]='c'; }
int main(int argc, char* argv[]) {
    char *pc = nullptr;
    int *ic = nullptr;
    bool b = nullptr;
    foo(nullptr);
  return 0;
}
'''

cpp_tests['strongly-typed enum']= '''
enum class Enum2 : unsigned int {Val1, Val2};
enum class Enum3 : unsigned long {Val1=17, Val2};
int main(int argc, char* argv[]) {
  return 0;
}
'''

cpp_tests['right angle brackets'] = '''
#include <vector>
int main(int argc, char* argv[]) {
  std::vector<std::vector<int>> blah;
  return 0;
}
'''


# explicit conversion operators??


cpp_tests['alias templates']= '''
template<typename First,typename Second, int third> class SomeType;
template<typename Second>
using typedefname= SomeType<float,Second,5>;

int main(int argc, char* argv[]) {
  return 0;
}
'''



cpp_tests['using syntax instead of typedefs']= '''
using OtherType=void (*)(double);
int main(int argc, char* argv[]) {
  return 0;
}
'''


cpp_tests['unrestricted unions']= '''
//for placement new
#include <new>
 
struct Point  {
    Point() {}
    Point(int x, int y): x_(x), y_(y) {}
    int x_, y_;
};
union U {
    int z;
    double w;
    Point p;  // Illegal in C++03; point has a non-trivial constructor.  However, this is legal in C++11.
    U() { new( &p ) Point(); } // No nontrivial member functions are implicitly defined for a union;
                               // if required they are instead deleted to force a manual definition.
};
int main(int argc, char* argv[]) {
  return 0;
}
'''


cpp_tests['templates with variable number of values']= '''
template<typename... Values> class ntuple;
int main(int argc, char* argv[]) {
  return 0;
}
'''


cpp_tests['new string literals']= '''

int main(int argc, char* argv[]) {
    auto s0 = u8"I'm a UTF-8 string.";
    auto s1 = u"A UTF-16 string";
    auto s2 = U"This is a UTF-32 string";
    auto s3 = R"(The raw string)";
  return 0;
}
'''


cpp_tests['user-defined literals']= '''
#include <string>
struct Sequence {
    std::string blah_;
    Sequence(const char* literal_string) : blah(literal_string) {}
};
Sequence operator "" seq(const char* literal) { return Sequence(literal); }
int main(int argc, char* argv[]) {
    auto my_seq = ACGT_seq;
  return 0;
}
'''

# multitasking memory model???

# thread-local storage ???


cpp_tests['explicitly defaulted special member functions']= '''
struct SomeType {
    int val_;
    SomeType() = default; //The default constructor is explicitly stated.
    SomeType(int value) : val_(value){};
};
int main(int argc, char* argv[]) {
    SomeType s;
  return 0;
}
'''



cpp_tests['explicitly deleted member functions']= '''
struct NonCopyable {
    NonCopyable & operator=(const NonCopyable&) = delete;
    NonCopyable(const NonCopyable&) = delete;
    NonCopyable() = default;
};
int main(int argc, char* argv[]) {
    NonCopyable n;
  return 0;
}
'''


cpp_tests['long long int']= '''
int main(int argc, char* argv[]) {
    long long int alfdjasflhsafdlh;
  return 0;
}
'''


cpp_tests['static_assert']= '''
#include <memory>
int main(int argc, char* argv[]) {
    static_assert(sizeof(size_t)==sizeof(int*), "pointer and size_t do not match");
  return 0;
}
'''


cpp_tests['sizeof on member objects']= '''
#include <memory>
struct SomeType {
    float member;
};
int main(int argc, char* argv[]) {
   size_t  b = sizeof(SomeType::member);
  return 0;
}
'''


cpp_tests['tuple']= '''
#include <tuple>
int main(int argc, char* argv[]) {
    std::tuple<int,double> blah(3,7.5);
  return 0;
}
'''


cpp_tests['hash tables']= '''
#include <unordered_set>
int main(int argc, char* argv[]) {
    std::unordered_set s;
  return 0;
}
'''


cpp_tests['regex']= '''
#include <regex>
int main(int argc, char* argv[]) {
    std::regex rgx("[\\t\\n]");
  return 0;
}
'''


cpp_tests['shared_ptr']= '''
#include <memory>
int main(int argc, char* argv[]) {
    std::shared_ptr p(new int[3]);
  return 0;
}
'''


cpp_tests['random numbers']= '''
#include <random>
int main(int argc, char* argv[]) {
    std::mt19937 engine;
  return 0;
}
'''


cpp_tests['wrapper reference']= '''
#include <iostream>
#include <functional>
// This function will obtain a reference to the parameter 'r' and increment it.
void f (int &r)  { r++; }
 
// Template function.
template<class F, class P> void g (F f, P t)  { f(t); }
 
int main()
{
    int i = 0 ;
    g (f, i) ;  // 'g<void (int &r), int>' is instantiated
               // then 'i' will not be modified.
    std::cout << i << std::endl;  // Output -> 0
 
    g (f, std::ref(i));  // 'g<void(int &r),reference_wrapper<int>>' is instantiated
                    // then 'i' will be modified.
    std::cout << i << std::endl;  // Output -> 1
    return 0;
}
'''


cpp_tests['polymorphic wrappers for function objects']= '''
#include <algorithm>
#include <functional>
int main(int argc,char* argv[]) {
std::function<int (int, int)> func;  // Wrapper creation using
                                 // template class 'function'.
std::plus<int> add;  // 'plus' is declared as 'template<class T> T plus( T, T ) ;'
                 // then 'add' is type 'int add( int x, int y )'.
func = add;  // OK - Parameters and return types are the same.
 
int a = func (1, 2);  // NOTE: if the wrapper 'func' does not refer to any function,
                      // the exception 'std::bad_function_call' is thrown.
 
std::function<bool (short, short)> func2 ;
if(!func2) { // True because 'func2' has not yet been assigned a function.
 
    bool adjacent(long x, long y);
    func2 = &adjacent ;  // OK - Parameters and return types are convertible.
 
    struct Test {
        bool operator()(short x, short y);
    };
    Test car;
    func = std::ref(car);  // 'std::ref' is a template function that returns the wrapper
                     // of member function 'operator()' of struct 'car'.
}
func = func2;  // OK - Parameters and return types are convertible.
return 0;
}
'''


cpp_tests['type traits metaprogramming']= '''
#include <type_traits>
// First way of operating.
template< bool B > struct Algorithm {
    template<class T1, class T2> static int do_it (T1 &a, T2 &b)  { return a+b; }
};
 
// Second way of operating.
template<> struct Algorithm<true> {
    template<class T1, class T2> static int do_it (T1 a, T2 b)  { return a+b; }
};
 
// Instantiating 'elaborate' will automatically instantiate the correct way to operate.
template<class T1, class T2>
int elaborate (T1 A, T2 B)
{
    // Use the second way only if 'T1' is an integer and if 'T2' is
    // in floating point, otherwise use the first way.
    return Algorithm<std::is_integral<T1>::value && std::is_floating_point<T2>::value>::do_it( A, B ) ;
}

int main(int argc, char* argv[]) {
  return 0;
}
'''


custom_tests = {
     'CheckCPP11' : SConsCheck.CheckCPP11()
    }
for name,t in cpp_tests.items():
    custom_tests[name.replace(' ','_')]=SConsCheck.CheckSnippet(name,t)


conf = Configure(env, custom_tests)

if GetOption('echo'):
    conf.logstream = sys.stdout

if not conf.CheckCXX():
    logger.debug('CXX %s' % env['CXX'])
    logger.debug('CXXCOM %s' % env['CXXCOM'])
    logger.error('The compiler isn\'t compiling.')
    Exit(1)

failure_cnt=0

if not conf.CheckCPP11():
    logger.error('Compiler does not support c++0x standard.')
    Exit(1)

for test in sorted(cpp_tests.keys()):   
    attr=conf.__getattribute__(test.replace(' ','_'))
    if not attr.__call__():
        failure_cnt+=1

    
env = conf.Finish()

cfg.write('used.cfg')
