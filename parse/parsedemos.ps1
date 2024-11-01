$files = Get-ChildItem -Path "demos"
foreach ($file in $files) {
    go run parse.go $file
}