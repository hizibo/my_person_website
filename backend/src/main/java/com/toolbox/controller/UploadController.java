package com.toolbox.controller;

import com.toolbox.common.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/upload")
@Tag(name = "文件上传")
@CrossOrigin(origins = "*")
public class UploadController {

    @Value("${upload.path:/uploads}")
    private String uploadPath;

    @Value("${upload.url-prefix:/uploads}")
    private String urlPrefix;

    @PostMapping("/image")
    @Operation(summary = "上传图片")
    public Result<Map<String, String>> uploadImage(@RequestParam("file") MultipartFile file) {
        // 验证文件
        if (file.isEmpty()) {
            return Result.error("文件不能为空");
        }

        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null) {
            return Result.error("文件名不能为空");
        }

        // 检查文件类型
        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("image/")) {
            return Result.error("只支持上传图片文件");
        }

        // 检查文件大小（最大 10MB）
        long maxSize = 10 * 1024 * 1024;
        if (file.getSize() > maxSize) {
            return Result.error("图片大小不能超过 10MB");
        }

        try {
            // 生成存储路径：/uploads/images/2026/04/23/xxx.jpg
            String datePath = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy/MM/dd"));
            String fileExtension = getFileExtension(originalFilename);
            String newFileName = UUID.randomUUID().toString().replace("-", "") + fileExtension;
            
            // 相对路径（用于数据库存储和URL访问）
            String relativePath = "/images/" + datePath + "/" + newFileName;
            
            // 绝对路径（用于文件存储）
            Path absolutePath = Paths.get(uploadPath, relativePath);
            
            // 创建目录
            Files.createDirectories(absolutePath.getParent());
            
            // 保存文件
            file.transferTo(absolutePath.toFile());
            
            // 返回访问URL
            Map<String, String> result = new HashMap<>();
            result.put("url", urlPrefix + relativePath);
            result.put("filename", newFileName);
            result.put("originalName", originalFilename);
            result.put("size", String.valueOf(file.getSize()));
            
            return Result.success(result);
        } catch (IOException e) {
            e.printStackTrace();
            return Result.error("文件上传失败：" + e.getMessage());
        }
    }

    /**
     * 获取文件扩展名
     */
    private String getFileExtension(String filename) {
        int lastDotIndex = filename.lastIndexOf(".");
        if (lastDotIndex > 0) {
            return filename.substring(lastDotIndex).toLowerCase();
        }
        return "";
    }
}
