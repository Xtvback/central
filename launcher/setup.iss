#define MyAppName "Central Launcher"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Central Criativa"
#define MyAppExeName "CentralLauncher.exe"

[Setup]
AppId={{B51A1F98-3A05-43F1-9017-378E16DE13C8}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\Central Launcher
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=CentralLauncher_Setup_1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar um atalho no ambiente de trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Files]
Source: "dist\CentralLauncher.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Central Launcher"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Central Launcher"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir Central Launcher"; Flags: nowait postinstall skipifsilent
