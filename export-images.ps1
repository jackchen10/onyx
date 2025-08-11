#!/usr/bin/env pwsh
# Docker镜像导出脚本
# 用于创建可分发的镜像包

param(
    [string]$OutputDir = "docker-images",
    [switch]$Compress = $false,
    [switch]$Clean = $false
)

# 颜色输出函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Error { Write-ColorOutput Red $args }
function Write-Info { Write-ColorOutput Cyan $args }

# 检查Docker环境
function Test-DockerEnvironment {
    try {
        docker version | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Docker未运行"
        }
        Write-Success "✅ Docker环境正常"
    } catch {
        Write-Error "❌ Docker未运行，请启动Docker Desktop"
        exit 1
    }
}

# 获取项目镜像列表
function Get-ProjectImages {
    Write-Info "🔍 获取项目镜像列表..."
    
    # 构建镜像（如果不存在）
    $images = @()
    
    # 检查项目镜像是否存在
    $projectImages = @(
        "onyx-api",
        "onyx-web", 
        "onyx-model-server",
        "onyx-worker"
    )
    
    foreach ($image in $projectImages) {
        $exists = docker images -q $image 2>$null
        if ($exists) {
            $images += $image
            Write-Success "✅ 找到镜像: $image"
        } else {
            Write-Warning "⚠️ 镜像不存在: $image"
        }
    }
    
    # 基础镜像
    $baseImages = @(
        "postgres:14-alpine",
        "redis:7-alpine",
        "nginx:alpine",
        "python:3.11-slim",
        "node:18-alpine"
    )
    
    foreach ($image in $baseImages) {
        $exists = docker images -q $image 2>$null
        if ($exists) {
            $images += $image
            Write-Success "✅ 找到基础镜像: $image"
        } else {
            Write-Info "📥 拉取基础镜像: $image"
            docker pull $image
            if ($LASTEXITCODE -eq 0) {
                $images += $image
            }
        }
    }
    
    return $images
}

# 导出镜像
function Export-Images {
    param([array]$Images)
    
    Write-Info "📦 开始导出Docker镜像..."
    
    # 创建导出目录
    if ($Clean -and (Test-Path $OutputDir)) {
        Remove-Item -Recurse -Force $OutputDir
    }
    
    if (!(Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
    
    $totalSize = 0
    $exportedImages = @()
    
    foreach ($image in $Images) {
        $filename = "$OutputDir/$($image -replace ':', '_' -replace '/', '_').tar"
        Write-Info "📤 导出镜像: $image -> $filename"
        
        try {
            docker save -o $filename $image
            if ($LASTEXITCODE -eq 0) {
                $fileSize = (Get-Item $filename).Length
                $totalSize += $fileSize
                $exportedImages += @{
                    Name = $image
                    File = $filename
                    Size = $fileSize
                }
                Write-Success "✅ 成功导出: $image ($([math]::Round($fileSize / 1MB, 2)) MB)"
            } else {
                Write-Error "❌ 导出失败: $image"
                if (Test-Path $filename) {
                    Remove-Item $filename
                }
            }
        } catch {
            Write-Error "❌ 导出异常: $image - $_"
        }
    }
    
    Write-Success "🎉 镜像导出完成!"
    Write-Info "📊 导出统计:"
    Write-Info "   - 成功导出: $($exportedImages.Count) 个镜像"
    Write-Info "   - 总大小: $([math]::Round($totalSize / 1MB, 2)) MB"
    
    return $exportedImages
}

# 创建导入脚本
function New-ImportScript {
    param([array]$ExportedImages)
    
    Write-Info "📝 创建导入脚本..."
    
    $importScript = @"
#!/usr/bin/env pwsh
# Docker镜像导入脚本
# 自动生成于: $(Get-Date)

param(
    [switch]`$Verbose = `$false
)

function Write-ColorOutput(`$ForegroundColor) {
    `$fc = `$host.UI.RawUI.ForegroundColor
    `$host.UI.RawUI.ForegroundColor = `$ForegroundColor
    if (`$args) {
        Write-Output `$args
    } else {
        `$input | Write-Output
    }
    `$host.UI.RawUI.ForegroundColor = `$fc
}

function Write-Success { Write-ColorOutput Green `$args }
function Write-Info { Write-ColorOutput Cyan `$args }
function Write-Error { Write-ColorOutput Red `$args }

Write-Success "📥 开始导入Docker镜像..."

# 检查Docker环境
try {
    docker version | Out-Null
    if (`$LASTEXITCODE -ne 0) {
        throw "Docker未运行"
    }
} catch {
    Write-Error "❌ Docker未运行，请启动Docker Desktop"
    exit 1
}

# 导入镜像
`$images = Get-ChildItem -Path "." -Filter "*.tar" | Sort-Object Name
`$imported = 0
`$failed = 0

foreach (`$image in `$images) {
    Write-Info "📥 导入镜像: `$(`$image.Name)"
    
    try {
        if (`$Verbose) {
            docker load -i `$image.FullName
        } else {
            docker load -i `$image.FullName | Out-Null
        }
        
        if (`$LASTEXITCODE -eq 0) {
            `$imported++
            Write-Success "✅ 成功导入: `$(`$image.Name)"
        } else {
            `$failed++
            Write-Error "❌ 导入失败: `$(`$image.Name)"
        }
    } catch {
        `$failed++
        Write-Error "❌ 导入异常: `$(`$image.Name) - `$_"
    }
}

Write-Success "🎉 镜像导入完成!"
Write-Info "📊 导入统计:"
Write-Info "   - 成功导入: `$imported 个镜像"
Write-Info "   - 失败: `$failed 个镜像"

if (`$failed -eq 0) {
    Write-Success "✅ 所有镜像导入成功，可以开始部署应用"
    Write-Info "💡 使用以下命令启动应用:"
    Write-Info "   docker-compose up -d"
} else {
    Write-Error "❌ 部分镜像导入失败，请检查错误信息"
}
"@

    $importScript | Out-File -FilePath "$OutputDir/import-images.ps1" -Encoding UTF8
    
    # 创建镜像清单
    $manifest = @"
# Docker镜像清单
# 生成时间: $(Get-Date)

## 包含的镜像

| 镜像名称 | 文件名 | 大小 (MB) |
|----------|--------|-----------|
"@

    foreach ($img in $ExportedImages) {
        $sizeMB = [math]::Round($img.Size / 1MB, 2)
        $fileName = Split-Path $img.File -Leaf
        $manifest += "`n| $($img.Name) | $fileName | $sizeMB |"
    }
    
    $manifest += @"

## 使用说明

1. 确保Docker Desktop已安装并运行
2. 运行导入脚本:
   ```powershell
   .\import-images.ps1
   ```
3. 启动应用:
   ```powershell
   docker-compose up -d
   ```

## 系统要求

- Windows 10/11 with Docker Desktop
- 最少8GB RAM
- 最少20GB可用磁盘空间
- WSL2支持

总镜像大小: $([math]::Round(($ExportedImages | Measure-Object -Property Size -Sum).Sum / 1MB, 2)) MB
"@

    $manifest | Out-File -FilePath "$OutputDir/README.md" -Encoding UTF8
    
    Write-Success "✅ 导入脚本和说明文档已创建"
}

# 压缩镜像包
function Compress-ImagePackage {
    if ($Compress) {
        Write-Info "🗜️ 压缩镜像包..."
        
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $archiveName = "onyx-docker-images-$timestamp.zip"
        
        try {
            Compress-Archive -Path "$OutputDir/*" -DestinationPath $archiveName -CompressionLevel Optimal
            $archiveSize = (Get-Item $archiveName).Length
            
            Write-Success "✅ 压缩完成: $archiveName"
            Write-Info "📦 压缩包大小: $([math]::Round($archiveSize / 1MB, 2)) MB"
            
            return $archiveName
        } catch {
            Write-Error "❌ 压缩失败: $_"
        }
    }
    
    return $null
}

# 显示使用说明
function Show-Usage {
    Write-Info "📋 使用说明:"
    Write-Info ""
    Write-Info "1. 分发镜像包:"
    Write-Info "   - 复制 '$OutputDir' 目录到目标机器"
    Write-Info "   - 或使用压缩包进行分发"
    Write-Info ""
    Write-Info "2. 在目标机器上导入:"
    Write-Info "   cd $OutputDir"
    Write-Info "   .\import-images.ps1"
    Write-Info ""
    Write-Info "3. 启动应用:"
    Write-Info "   docker-compose up -d"
    Write-Info ""
    Write-Info "💡 提示: 使用 -Compress 参数可以创建压缩包便于分发"
}

# 主函数
function Main {
    Write-Success "📦 Docker镜像导出工具"
    Write-Info "输出目录: $OutputDir"
    
    Test-DockerEnvironment
    
    $images = Get-ProjectImages
    if ($images.Count -eq 0) {
        Write-Error "❌ 未找到任何镜像，请先构建项目镜像"
        Write-Info "💡 运行以下命令构建镜像:"
        Write-Info "   .\deploy.ps1 -Action build"
        exit 1
    }
    
    $exportedImages = Export-Images -Images $images
    
    if ($exportedImages.Count -gt 0) {
        New-ImportScript -ExportedImages $exportedImages
        $archive = Compress-ImagePackage
        Show-Usage
        
        Write-Success "🎉 镜像导出完成!"
        Write-Info "📁 输出目录: $OutputDir"
        if ($archive) {
            Write-Info "📦 压缩包: $archive"
        }
    } else {
        Write-Error "❌ 没有成功导出任何镜像"
        exit 1
    }
}

# 错误处理
trap {
    Write-Error "❌ 脚本执行出错: $_"
    exit 1
}

# 执行主函数
Main
