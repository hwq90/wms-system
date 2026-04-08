# Access数据库转Excel脚本
$accdbPath = "C:\Users\Administrator\.openclaw\media\qqbot\downloads\仓库管理系统2026版本_1774153119155.accdb"
$excelPath = "C:\Users\Administrator\.openclaw\media\qqbot\downloads\仓库管理系统2026版本.xlsx"

Write-Host "开始转换..." -ForegroundColor Green
Write-Host "源文件: $accdbPath"
Write-Host "目标文件: $excelPath"

try {
    # 创建Excel应用程序对象
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    
    # 创建新的工作簿
    $workbook = $excel.Workbooks.Add()
    
    # 连接到Access数据库
    $conn = New-Object -ComObject ADODB.Connection

    $conn.Open("Provider=Microsoft.ACE.OLEDB.12.0;Data Source=$accdbPath")
    
    # 获取所有表名

    $schema = $conn.OpenSchema(20) # 20 = adSchemaTables

    $tables = @()

    while (!$schema.EOF) {

        $tableType = $schema.Fields["TABLE_TYPE"].Value

        $tableName = $schema.Fields["TABLE_NAME"].Value

        if ($tableType -eq "TABLE") {

            $tables += $tableName

        }

        $schema.MoveNext()

    }
    
    Write-Host "发现 $($tables.Count) 个表" -ForegroundColor Yellow
    
    # 为每个表创建一个工作表并导入数据

    foreach ($table in $tables) {

        Write-Host "处理表: $table" -ForegroundColor Cyan



        # 添加工作表

        $worksheet = $workbook.Worksheets.Add()

        $worksheet.Name = $table



        # 查询表数据

        $recordset = New-Object -ComObject ADODB.Recordset

        $recordset.Open("SELECT * FROM [$table]", $conn)



        # 写入列标题

        $col = 1

        for ($i = 0; $i -lt $recordset.Fields.Count; $i++) {

            $worksheet.Cells.Item(1, $col) = $recordset.Fields($i).Name

            $col++

        }



        # 写入数据行

        $row = 2

        while (!$recordset.EOF) {

            $col = 1

            for ($i = 0; $i -lt $recordset.Fields.Count; $i++) {

                $value = $recordset.Fields($i).Value

                $worksheet.Cells.Item($row, $col) = $value

                $col++

            }

            $recordset.MoveNext()

            $row++

        }

    }
    
    # 保存Excel文件

    $workbook.SaveAs($excelPath, 51) # 51 = xlOpenXMLWorkbook (xlsx)

    $workbook.Close()

    $excel.Quit()

    
    Write-Host "转换完成!" -ForegroundColor Green

    Write-Host "文件已保存到: $excelpath" -ForegroundColor Yellow

} catch {

    Write-Host "转换失败: $_" -ForegroundColor Red

}

finally {

    # 清理COM对象

    [System.Runtime.Interopservices.Marshal]::ReleaseComObject([System.__ComObject]$excel) | Out-Null

    [System.GC]::Collect()

    [System.GC]::WaitForPendingFinalizers()

}