[Setup]
AppName=RentMaster CRM
AppVersion=0.1.0
DefaultDirName={pf}\RentMaster CRM
DefaultGroupName=RentMaster CRM
UninstallDisplayIcon={app}\start_crm.bat
OutputBaseFilename=RentMasterCRMSetup
OutputDir=..\installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist_app\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\RentMaster CRM"; Filename: "{app}\start_crm.bat"
Name: "{commondesktop}\RentMaster CRM"; Filename: "{app}\start_crm.bat"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\start_crm.bat"; Description: "Start RentMaster CRM"; Flags: postinstall nowait skipifsilent

