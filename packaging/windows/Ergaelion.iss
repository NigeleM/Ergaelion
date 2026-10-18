; Inno Setup script for the Windows installer. The build passes the version and the program path:
;   ISCC /DMyAppVersion=1.0.0 /DMyBinary=dist\Ergaelion-windows-amd64.exe packaging\windows\Ergaelion.iss

#define MyAppName "Ergaelion"
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#ifndef MyBinary
  #define MyBinary "..\..\dist\Ergaelion-windows-amd64.exe"
#endif

[Setup]
AppId={{5E0C7A4B-3D2F-4B8E-9A61-7C2D9F3E8B10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppName}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
MinVersion=10.0
LicenseFile=..\..\LICENSE.txt
OutputDir=..\..\dist
OutputBaseFilename=Ergaelion-{#MyAppVersion}-windows-setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
ChangesEnvironment=yes
UninstallDisplayName={#MyAppName}

[Tasks]
Name: "addpath"; Description: "Add Ergaelion to the PATH, so you can run it from any terminal"; Flags: checkedonce

[Files]
Source: "{#MyBinary}"; DestDir: "{app}"; DestName: "Ergaelion.exe"; Flags: ignoreversion
Source: "..\..\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Code]
const
  EnvironmentKey = 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment';

procedure AddToPath(Dir: string);
var
  Current: string;
begin
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', Current) then
    if Pos(';' + Uppercase(Dir) + ';', ';' + Uppercase(Current) + ';') = 0 then
      RegWriteExpandStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', Current + ';' + Dir);
end;

procedure RemoveFromPath(Dir: string);
var
  Current: string;
begin
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', Current) then
  begin
    StringChangeEx(Current, ';' + Dir, '', True);
    StringChangeEx(Current, Dir + ';', '', True);
    RegWriteExpandStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', Current);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('addpath') then
    AddToPath(ExpandConstant('{app}'));
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    RemoveFromPath(ExpandConstant('{app}'));
end;
