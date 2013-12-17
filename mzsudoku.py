# coding: utf8
'''
Name: mzsudoku
partially from http://freepythontips.wordpress.com/2013/09/01/sudoku-solver-in-python/

Use mzsudoku.py as script
-- or --
mzsudoku.run('207006100000...') # 81 characters
or run subparts of .run(): .p(), .pp(), .n(), .r()
help(mzsudoku.run) or see run() code for details
''' 

import sys
import itertools

sudoku = ""   # last state

finished = False
failure = False

def same_row(i,j): return (i/9 == j/9)
def same_col(i,j): return (i-j) % 9 == 0
def same_block(i,j): return (i/27 == j/27 and i%9/3 == j%9/3)

def fill(number, row, col):
    '''will set number to the given position and then continue .run()
    works for suspended solution: mzsudoku.sudoku must exist 
    in mzsudoku.sudoku must be '0' on the given position
    row,col - 1..9
    '''
    if sudoku:
        pos = 9*(row-1)+col-1
        number = str(number)[-1:]
        if not number in '123456789':
            print 'digit 1..9 required as first parameter'
            return
        global sudoku
        if sudoku[pos]=='0':
            sudoku = sudoku[:pos] + number + sudoku[pos+1:]
            print sudoku 
        else:
            print "not '0' on required position"
    else:
        print "not suspended; run .run() first"

def run(setting, out='pnr'):
    '''setting: 81-characters string, 0 for unknown numbers
    out: mark possibilities(p), find n-combinations(n), find result(r)
    in addition to pnr, out can contain:
     = show definitely known numbers (otherwise show only unknown-possibilities)
     A apply known new numbers and cycle again
     a apply known new numbers after pressing Enter (anything else will quit)
    '''
    
    global sudoku
    setting = setting or sudoku
    if len(setting)!=81:
        print 'string with 81 positions required (0 for unknown digits)'
        return
    
    force = False
    while True:
        n_to_apply = []
        marked = p(setting)                # mark possibilities
        if 'p' in out:
            pp(marked, '=' in out)         # print possibilities as table
        n(marked, 'n' in out, n_to_apply, force)  # localize hidden n-combinations
        if finished:
            print
            print "FINISHED."
            break
        if failure:
            print
            print "FAILURE IN SETTING."
            break
        if not 'a' in out.lower():
            break
        setting2 = apply_known(setting, marked, n_to_apply)
        if setting==setting2:
            if force:
                print ("Cannot find algorithmical solution. "
                      "Try set something with .fill() method.")
                break
            else:
                force = True
                print "No easy solution - need to identify N-groups."
        else:
            force = False
        if 'a' in out and raw_input(): 
            break
        setting = setting2
    sudoku = setting
    if '0' in sudoku:
        print "suspended; use .fill(digit, row, col) and/or .run('', out)"
    print sudoku
    if 'r' in out and '0' in sudoku:
        #http://freepythontips.wordpress.com/2013/09/01/sudoku-solver-in-python/
        r(setting)   # solve based on recursive algorithmus from link above

def p(a):
    '''mark possibilities'''
    global finished
    finished = True
    marked = []
    for i in xrange(81):
        if a[i]=='0':
            excluded_numbers = set()
            for j in xrange(81):
                if a[j]!='0' and (
                          same_row(i,j) or same_col(i,j) or same_block(i,j)):
                    excluded_numbers.add(a[j])
            marked.append(excluded_numbers)
            finished = False
        else:
            marked.append(a[i])
    return marked

def n(marked, print_result, n_to_apply, force):
    '''print where n-sets are inside possibilities'''
    while True:
        resolve = False
        to_print = []
        for ln in xrange(9):
            block_pos = []
            block = []
            excluded = []
            for cl in xrange(9):
                pos = 9*ln + cl
                if isinstance(marked[pos], set):
                    block.append(marked[pos])
                    block_pos.append(pos)
                else:
                    excluded.append(marked[pos])
            resolve = solveN('ln%s'%(ln+1), block, excluded,
                  block_pos, n_to_apply, to_print, marked, print_result, force)
            if resolve:
                break
        if resolve:
            continue     
        for cl in xrange(9):
            block_pos = []
            block = []
            excluded = []
            for ln in xrange(9):
                pos = 9*ln + cl
                if isinstance(marked[pos], set):
                    block.append(marked[pos])
                    block_pos.append(pos)
                else:
                    excluded.append(marked[pos])
            resolve = solveN('cl%s'%(cl+1), block, excluded,         
                  block_pos, n_to_apply, to_print, marked, print_result, force)         
            if resolve:
                break
        if resolve:
            continue     
        for bl in xrange(9):
            block_pos = []
            hor = bl/3
            vert = bl%3 
            block = []
            excluded = []
            for ln in xrange(3*hor, 3*(hor+1)):
                for cl in xrange(3*vert, 3*(vert+1)):
                    pos = 9*ln + cl
                    if isinstance(marked[pos], set):
                        block.append(marked[pos])
                        block_pos.append(pos)
                    else:
                        excluded.append(marked[pos])
            resolve = solveN('bl%s'%(bl+1), block, excluded,
                  block_pos, n_to_apply, to_print, marked, print_result, force)         
            if resolve:
                break
        if not resolve:
            break
    if print_result and to_print:      
        print "hidden n-combinations"
        print ("[where / which numbers / field position "
                        "(counted from unknown)]:")
        for line in to_print:
            for item in line:
                print item,
            print

def solveN(symbol, block, excluded, block_pos, n_to_apply, to_print, marked,
                                                    print_result, force):
    #print symbol, len(block), excluded
    global failure
    resolve = False 
    included = []
    for number in '123456789':
        if not number in excluded:
            included.append(number)
    for lenN in xrange(len(block)-1, 0, -1):
        for candidate in itertools.combinations(included, lenN):
            where = []
            for i, fld in enumerate(block):
                for number in candidate:
                    if number not in fld:
                        where.append(i+1)
                        break
                if len(where)>lenN:
                    break
            else:
                print_append = [symbol, candidate, where]                
                if len(where)==1:
                    to_append = (candidate, block_pos[where[0]-1])
                    if not to_append in n_to_apply: 
                        n_to_apply.append(to_append)
                elif force:
                    # resolves all N-groups; this however lead usualy to lot
                    #   of additional information (and solution,
                    #   if easy possible), so we use this if previous step
                    #   wasn't sucessfull only
                    removed = set()
                    for where1 in where:
                        #fld = block[where1-1]
                        pos = block_pos[where1-1] 
                        for number in included:
                            if not number in candidate and not number in marked[pos]:
                                resolve = True
                                removed.add(number)
                                marked[pos].add(number)
                    if removed and print_result:
                        print symbol, where, 'removed:', removed
                if len(where)<lenN:
                    failure = True
                    print_append.append('WARNING: in %s fields only' % len(where))
                to_print.append(print_append)
    return resolve  

def pp(marked, show_fixed=False):
    '''print marked possibilities'''
    for ln in xrange(36):
        row = ln/4
        subln = ln%4 
        if subln:
            psub(subln, row, marked, show_fixed)
        else:
            ppl()
    ppl()

def psub(subln, row, marked, show_fixed=False):
    for cl in xrange(36):
        subcl = cl%4
        if subcl:
            pos = 9*row + cl/4
            if isinstance(marked[pos], set):
                subnum = str(3*(subln-1) + subcl)
                if subnum in marked[pos]:
                    ppskip()
                else:
                    pppossible(subnum) 
            elif subcl==1:
                if subln==2:
                    ppfixed(marked[pos], show_fixed)
                else:
                    ppspace()
        else:
            ppvertsep()
    ppvertsep()
    pplinesep()

def ppl():
    print 9*'+-------' + '+'
               
def ppskip():
    print ' ',

def pppossible(subnum):
    print subnum, 

def ppvertsep():
    print '|',

def pplinesep():
    print

def ppfixed(symbol, show_fixed=False):
    if show_fixed:
        #print '* %s *' % symbol,
        #print ' _%s_ ' % symbol,
        print ' = %s ' % symbol,
    else:
        ppspace()

def ppspace():
    print 5*' ',

def r(a):
    '''find solution
    from http://freepythontips.wordpress.com/2013/09/01/sudoku-solver-in-python/
    mz change: #mz'''
    i = a.find('0')
    if i == -1:
        print a
        return
  
    excluded_numbers = set()
    for j in xrange(81):
        #mz ++  a[j] and (....)  to avoid '0' in excluded_numbers  
        if a[j]!='0' and (
                      same_row(i,j) or same_col(i,j) or same_block(i,j)):
            excluded_numbers.add(a[j])
  
    for m in '123456789':
        if m not in excluded_numbers:
            r(a[:i]+m+a[i+1:])

def apply_known(setting, marked, n_to_apply):
    # apply naked singles
    setting2 = ''
    for i, fld in enumerate(marked):
        if len(fld)==8:
            for number in '123456789':
                if not number in fld:
                    setting2 += number
                    break
            continue   # setting2 enlarged already
        setting2 += setting[i]

    # apply hidden singles (obtained from n())
    for candidate, pos in n_to_apply:
        if setting2[pos]=='0':
            setting2 = setting2[:pos] + candidate[0] + setting2[pos+1:]    

    return setting2

if __name__ == '__main__':
    if len(sys.argv)>=2 and len(sys.argv[1]) == 81:
        run(sys.argv[1], len(sys.argv)>=3 and sys.argv[2] or 'pnr')
    else:
        print 'Usage: python sudoku.py puzzle'
        print '''  where puzzle is an 81 character string 
               representing the puzzle read left-to-right,
               top-to-bottom, and 0 is a blank'''