BENCH_REPS    = 10
HELIB_INC     = 'helib/helib.h'
HELIB_USE     = "using namespace helib;\n"
HELIB_INCS    = ''
HELIB_LIBS    = '-l:libhelib.a -lntl -lpthread'
PALISADE_INC  = 'palisade.h'
PALISADE_INCS = '-I/usr/include/palisade/core -I/usr/include/palisade/pke'
PALISADE_LIBS = '-lPALISADEcore -lPALISADEpke'
PALISADE_USE  = "using namespace lbcrypto;\n"
