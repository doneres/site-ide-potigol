# --- Configurações do Atalho ---
$NomeDoAtalho = "Potigol Web IDE.url"
$URLDoSite = "https://ide-potigol-brasil.duckdns.org/"
$IconeDoSite = "https://ide-potigol-brasil.duckdns.org/static/logo_potigol.png" # Usando a logo do seu site

# --- Lógica do Script ---

$CaminhoDesktop = [System.Environment]::GetFolderPath('Desktop')
$CaminhoCompletoAtalho = Join-Path $CaminhoDesktop $NomeDoAtalho

$WshShell = New-Object -ComObject WScript.Shell
$Atalho = $WshShell.CreateShortcut($CaminhoCompletoAtalho)

$Atalho.TargetPath = $URLDoSite
$Atalho.IconLocation = $IconeDoSite

$Atalho.Save()

Write-Host "Atalho 'Potigol Web IDE' criado com sucesso na Área de Trabalho!"

Start-Process $URLDoSite

Write-Host "O site foi aberto no navegador padrão. Pressione Ctrl+D para favoritá-lo."
Read-Host "Pressione Enter para sair."