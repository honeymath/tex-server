"command! SyncCurl call SyncCurl()
"let g:pdflatex_cmd = 'pdflatex -synctex=1 -interaction=nonstopmode'
let g:syncpdf_script_path = expand('<sfile>:p:h')
let g:pdflatex_cmd = 'pdflatex -synctex=1'
let g:pdf_target_dir = expand('~/repositories/llmos/static')
let g:pdf_target_file = 'main.pdf'
let g:synccurl_cmd = 'bash ~/repositories/syncpdf-remote/synccurl.sh'

function! FindMainTex()
  let l:dir = expand('%:p:h')
  while 1
    let l:target = l:dir . '/main.tex'
    execute 'cd' . fnameescape(l:dir)
    if filereadable(l:target)
      return l:target
    endif
    let l:parent = fnamemodify(l:dir, ':h')
    if l:parent ==# l:dir
      return ''
    endif
    let l:dir = l:parent
  endwhile
endfunction


function! SoftSyncCurl()
  let l:file = expand('%:p')
  let l:line = line('.')
  let l:col = col('.')
  let l:filestamp = FindMainTex()
  "echo "Syncing: " . l:filestamp . " at line " . l:line . ", column " . l:col . " with filestamp: " . l:file
  let l:cmd = g:synccurl_cmd . ' ' . shellescape(l:filestamp) . ' ' . l:line . ' ' . l:col . ' ' . shellescape(l:file)  
  echo system(l:cmd)
endfunction

function! SyncCurl()
  let l:file = expand('%:p')
  let l:line = line('.')
  let l:col = col('.')
  let l:filestamp = FindMainTex()
  "echo "Syncing: " . l:filestamp . " at line " . l:line . ", column " . l:col . " with filestamp: " . l:file
  let l:cmd = g:synccurl_cmd . ' ' . shellescape(l:filestamp) . ' ' . l:line . ' ' . l:col . ' ' . shellescape(l:file) . ' ' . '-r'
"  echo system(l:cmd)
   execute 'silent !' . l:cmd
endfunction


function! CompileAndCopyMainPdf()
  " 1️⃣ 查找 main.tex
  let l:main_tex = FindMainTex()
  if empty(l:main_tex)
    echohl ErrorMsg | echo "main.tex not found" | echohl None
    return
  endif

  " 2️⃣ 执行 pdflatex
  let l:cmd = g:pdflatex_cmd . ' ' . shellescape(l:main_tex)
  echo "Running: " . l:cmd
  execute '!' . l:cmd
  redraw!
  "let l:output = system(l:cmd)
  if v:shell_error != 0
    echohl ErrorMsg | echo "pdflatex failed" | echohl None
    "echo l:output
    return
  endif

  " 3️⃣ 检查 PDF 是否存在
  let l:pdf_file = fnamemodify(l:main_tex, ':r') . '.pdf'
  if !filereadable(l:pdf_file)
    echohl ErrorMsg | echo "PDF not generated" | echohl None
    return
  endif

  " 4️⃣ 复制 PDF 到目标目录
"  if !isdirectory(g:pdf_target_dir)
"    call mkdir(g:pdf_target_dir, 'p')
"  endif
"  let l:dest = g:pdf_target_dir . '/' . g:pdf_target_file
"  let l:copy_cmd = 'cp ' . shellescape(l:pdf_file) . ' ' . shellescape(l:dest)
"  echo l:copy_cmd
"  call system(l:copy_cmd)
"  if v:shell_error == 0
"    echo "Copied to: " . l:dest
"  else
"    echohl ErrorMsg | echo "Failed to copy PDF" | echohl None
"  endif
" 4️⃣ 调用 paste.sh 脚本来复制 PDF
let l:paste_script = g:syncpdf_script_path . '/paste.sh'
let l:cmd = shellescape(l:paste_script) . ' ' . shellescape(l:pdf_file)

let l:result = system(l:cmd)
if v:shell_error == 0
  echo "✅ Paste success:"
  echo l:result
else
  echohl ErrorMsg
  echo "❌ Paste failed:"
  echo l:result
  echohl None
  return
endif
  " 5️⃣ 打Finally, call synccurl
  call SyncCurl()
endfunction

nnoremap ≤ :call CompileAndCopyMainPdf() <CR><CR>:redraw!<CR>
