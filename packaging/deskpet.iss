#define AppVersion "0.1.0"
[Setup]
AppId={{B1F3654D-65A4-43EF-B2DB-61B7B1337A19}
AppName=DeskPet
AppVersion={#AppVersion}
AppVerName=DeskPet {#AppVersion} beta
AppPublisher=Akuazzamq
DefaultDirName={localappdata}\Programs\DeskPet
DefaultGroupName=DeskPet
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
WizardStyle=modern
DisableProgramGroupPage=yes
DisableWelcomePage=no
OutputDir=..\dist
OutputBaseFilename=DeskPet-Setup
SetupIconFile=..\assets\deskpet.ico
UninstallDisplayIcon={app}\DeskPet.exe
LicenseFile=..\LICENSE
Compression=lzma2
SolidCompression=yes
CloseApplications=yes
RestartApplications=no
[Tasks]
Name: desktopicon; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"
[Files]
Source: "..\dist\DeskPet\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{userdesktop}\DeskPet"; Filename: "{app}\DeskPet.exe"; WorkingDir: "{app}"; IconFilename: "{app}\DeskPet.exe"; IconIndex: 0; Tasks: desktopicon
Name: "{userprograms}\DeskPet\DeskPet"; Filename: "{app}\DeskPet.exe"; WorkingDir: "{app}"; IconFilename: "{app}\DeskPet.exe"; IconIndex: 0
Name: "{userprograms}\DeskPet\Uninstall DeskPet"; Filename: "{uninstallexe}"
[Run]
Filename: "{app}\DeskPet.exe"; Description: "Open DeskPet dashboard"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Command: String;
begin
  if CurUninstallStep = usUninstall then
    if RegQueryStringValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Run', 'DeskPet', Command) then
      if Pos(Lowercase(ExpandConstant('{app}\DeskPet.exe')), Lowercase(Command)) > 0 then
        RegDeleteValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Run', 'DeskPet');
end;
