dotnet publish -r linux-x64 -c Release -o ../Releases/linux/evasion /p:SelfContained=true /p:PublishSingleFile=true /p:PublishReadyToRun=true
dotnet publish -r osx-x64 -c Release -o ../Releases/osx/evasion /p:SelfContained=true /p:PublishSingleFile=true /p:PublishReadyToRun=true
dotnet publish -r win-x64 -c Release -o ../Releases/win/evasion /p:SelfContained=true /p:PublishSingleFile=true /p:PublishReadyToRun=true