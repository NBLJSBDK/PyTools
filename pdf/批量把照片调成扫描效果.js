#target photoshop

// 设置源文件夹路径（改为你的文件夹路径）
var sourceFolder = new Folder("D:/西航/大三/复习/形势与政策/pdf/改");

// 设置目标文件夹路径（可以选择另一个文件夹用于保存处理后的图片）
var destFolder = new Folder("D:/西航/大三/复习/形势与政策/pdf/改_out");

if (!destFolder.exists) {
    destFolder.create(); // 如果目标文件夹不存在，创建它
}

// 获取所有 PNG 和 JPG 文件
var files = sourceFolder.getFiles(function(file) {
    return (file instanceof File) && (file.name.match(/\.(jpg|jpeg|png)$/i));
});

// 遍历每个文件
for (var i = 0; i < files.length; i++) {
    var file = files[i];
    
    try {
        // 打开文件
        var doc = open(file);
        
        // 解锁背景图层
        if (app.activeDocument.backgroundLayer) {
            app.activeDocument.backgroundLayer.isBackgroundLayer = false;
        }

        // 复制背景图层
        var backgroundLayer = app.activeDocument.layers[0];
        backgroundLayer.copy();

        // 新建图层并粘贴复制的图层
        var newLayer = app.activeDocument.artLayers.add();
        newLayer.name = "Blur Layer";
        app.activeDocument.paste();

        // 应用高斯模糊滤镜
        var radius = 100;
        app.activeDocument.activeLayer.applyGaussianBlur(radius);

        // 改变图层混合模式
        app.activeDocument.activeLayer.blendMode = BlendMode.DIVIDE;

        // 曲线调整部分（此部分需要手动进行对比度调整）
        // 由于自动调整曲线非常复杂且依赖具体图片内容，无法直接通过代码实现
        // 可以考虑用图像调整工具（如亮度/对比度）来代替，或手动进行调整

        // 合并所有图层
        app.activeDocument.flatten();

        // 保存处理后的图片到目标文件夹
        var saveFile = new File(destFolder + "/" + doc.name);
        
        // 保存为 PNG 或 JPG
        if (doc.name.match(/\.png$/i)) {
            var pngSaveOptions = new PNGSaveOptions();
            doc.saveAs(saveFile, pngSaveOptions, true);
        } else {
            var jpegSaveOptions = new JPEGSaveOptions();
            jpegSaveOptions.quality = 12; // 设置图片质量
            doc.saveAs(saveFile, jpegSaveOptions, true);
        }

        // 关闭当前文档，不保存更改
        doc.close(SaveOptions.DONOTSAVECHANGES);

    } catch (e) {
        // 如果遇到错误，显示错误信息并继续下一个文件
        alert("处理文件 " + file.name + " 时出错: " + e.message);
        continue; // 跳过当前文件，继续处理下一个文件
    }
}

alert("批处理完成！");
