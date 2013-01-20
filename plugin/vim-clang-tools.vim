au FileType c,cpp,objc,objcpp call <SID>ClangToolsInit()

" Store the plugin path, as this is only available when sourcing the file.
let s:plugin_path = escape(expand('<sfile>:p:h'), '\')

function! s:ClangToolsInit()
  let l:bufname = bufname("%")
  if l:bufname == ''
    return
  endif

  if !exists('g:clangtools_library_path')
    let g:clangtools_library_path = ''
  endif

  call s:initClangToolsPython()
endfunction

function! s:initClangToolsPython()
  " Only load the python script once.
  if !exists('s:python_loaded')
    python import sys
    exe 'python sys.path = ["' . s:plugin_path . '"] + sys.path'
    exe 'pyfile ' . s:plugin_path . '/vim_clang_tools.py'
    py vim.command('let l:res = ' + str(init_clang_tools(vim.eval('g:clangtools_library_path'))))
    if l:res == 0
      echoe 'clang_tools: Error loading the Python script.'
      return 0
    endif
    return 1
endfunction

function! ClangToolsGoToDefinition()
  let l:filename = expand('%:p')
  let l:line = line('.')
  let l:column = col('.')
  let l:newpos = getpos('.')
  py vim.command('let l:lineAndCol =' + str(go_to_definition(vim.eval('l:filename'), vim.eval('l:line'), vim.eval('l:column'))))
  let l:newpos[1] = lineAndCol[0]
  let l:newpos[2] = lineAndCol[1]
  call setpos('.', l:newpos)
endfunction

" vim: set ts=2 sts=2 sw=2 expandtab :    
