@echo off
chcp 65001 >nul
title 新建博客文章小助手
color 0A

echo ========================================
echo        欢迎使用 Xynrin's Blog 写作助手
echo ========================================
echo.

set /p folderName="请输入文章的英文或拼音缩写（将作为文件夹名称和网址）："
if "%folderName%"=="" goto error

set /p articleTitle="请输入文章标题（显示在网页上的中文标题）："
if "%articleTitle%"=="" goto error

:: 获取当前日期 YYYY-MM-DD
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set currentDate=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%

set "targetDir=content\post\%folderName%"
set "targetFile=%targetDir%\index.md"

if exist "%targetDir%" (
    echo.
    echo [错误] 文件夹 %folderName% 已经存在了！请换一个名字。
    pause
    exit
)

:: 创建文件夹
mkdir "%targetDir%"

:: 写入 Front Matter 模板
(
echo ---
echo title: "%articleTitle%"
echo date: %currentDate%
echo slug: "%folderName%"
echo description: ""
echo categories:
echo   - 随笔
echo tags:
echo   - 默认标签
echo draft: false
echo ---
echo.
echo 在这里开始写你的正文...
) > "%targetFile%"

echo.
echo [成功] 文章已创建： %targetFile%
echo 正在尝试使用系统默认编辑器打开它...

:: 尝试使用 VS Code 打开，如果不行则用记事本
code "%targetFile%" 2>nul
if %errorlevel% neq 0 (
    start notepad "%targetFile%"
)

exit

:error
echo [错误] 输入不能为空！
pause
exit
