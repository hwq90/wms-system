const XLSX = require('xlsx');
const wb = XLSX.utils.book_new();

// 物料库模板
const productData = [
    ['物料编码', '物料名称', '规格型号', '单位', '分类', '供应商', '库存下限', '库存上限', '单价', '默认库位', '保质期(天)', '批次管理', '物料状态'],
    ['A001', '螺丝M6×20mm', '6mm×20mm', '盒', '五金', '供应商A', 10, 1000, 2.5, 'A-01-01', 365, '否', '正常'],
    ['A002', '螺母M6', 'M6', '盒', '五金', '供应商A', 20, 2000, 1.0, 'A-01-02', 365, '否', '正常'],
    ['B001', '轴承608', '608', '个', '轴承', '供应商B', 5, 500, 15.0, 'B-01-01', 730, '否', '正常']
];
const ws1 = XLSX.utils.aoa_to_sheet(productData);
XLSX.utils.book_append_sheet(wb, ws1, '物料库');

// 库位模板
const locationData = [
    ['库位编码', '仓库', '区域', '货架', '层数', '库位类型', '容量', '备注'],
    ['A-01-01', '1号仓', 'A区', '01架', '1层', '常用', 100, '五金区'],
    ['A-01-02', '1号仓', 'A区', '01架', '2层', '常用', 100, '五金区'],
    ['B-01-01', '1号仓', 'B区', '01架', '1层', '常用', 50, '轴承区']
];
const ws2 = XLSX.utils.aoa_to_sheet(locationData);
XLSX.utils.book_append_sheet(wb, ws2, '库位');

// 领料清单模板
const pickData = [
    ['物料编码', '物料名称', '领取数量', '库位'],
    ['A001', '螺丝M6×20mm', 50, ''],
    ['A002', '螺母M6', 100, ''],
    ['B001', '轴承608', 20, '']
];
const ws3 = XLSX.utils.aoa_to_sheet(pickData);
XLSX.utils.book_append_sheet(wb, ws3, '领料清单');

XLSX.writeFile(wb, 'WMS导入模板.xlsx');
console.log('模板生成成功: WMS导入模板.xlsx');