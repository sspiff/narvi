
REM Copyright (c) 2014, Brian Boylston
REM All rights reserved.
REM 
REM Redistribution and use in source and binary forms, with or without
REM modification, are permitted provided that the following conditions are met:
REM 
REM * Redistributions of source code must retain the above copyright notice, this
REM   list of conditions and the following disclaimer.
REM 
REM * Redistributions in binary form must reproduce the above copyright notice,
REM   this list of conditions and the following disclaimer in the documentation
REM   and/or other materials provided with the distribution.
REM 
REM THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
REM AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
REM IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
REM DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
REM FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
REM DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
REM SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
REM CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
REM OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
REM OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



@set OUTFILE=scrypt-hash.dll

@set SCRYPTDIR=scrypt-1.1.6
@set SCRYPTLIBROOT=%SCRYPTDIR%\lib

@set OBJDIR=obj


mkdir %OBJDIR% || exit /b
copy config-Windows.h %OBJDIR%\config.h || exit /b
copy %SCRYPTDIR%\scrypt_platform.h %OBJDIR%\ || exit /b
copy %SCRYPTLIBROOT%\util\sysendian.h %OBJDIR%\ || exit /b
copy %SCRYPTLIBROOT%\crypto\sha256.h %OBJDIR%\ || exit /b
copy %SCRYPTLIBROOT%\crypto\sha256.c %OBJDIR%\ || exit /b
copy %SCRYPTLIBROOT%\crypto\crypto_scrypt.h %OBJDIR%\ || exit /b
copy %SCRYPTLIBROOT%\crypto\crypto_scrypt-ref.c %OBJDIR%\ || exit /b

cd %OBJDIR% || exit /b
cl.exe /O2 /D_USRDLL /D_WINDLL /DCONFIG_H_FILE=\"config.h\" /Dinline=__inline /c sha256.c
cl.exe /O2 /D_USRDLL /D_WINDLL /DCONFIG_H_FILE=\"config.h\" /Dinline=__inline /c crypto_scrypt-ref.c
link.exe /DLL /OUT:%OUTFILE% /EXPORT:crypto_scrypt sha256.obj crypto_scrypt-ref.obj
cd ..

