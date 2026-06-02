@echo off
start "" "C:\albion_online\game\Albion-Online_BE.exe"
start "" "C:\Users\Admin\Desktop\util\MacroCreator\MacroCreator.exe" "C:\Users\Admin\Desktop\util\MacroCreator\albionNN.pmc" -p
timeout /t 15 /nobreak
powershell -command "Start-Process 'C:\Users\Admin\Desktop\util\StatisticsAnalysis-AlbionOnline-v9.0.1-windows-x64\StatisticsAnalysisTool.exe' -Verb runAs"