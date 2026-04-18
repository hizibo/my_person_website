package com.toolbox.controller;

import com.toolbox.common.Result;
import com.toolbox.service.XmindService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@RestController
@RequestMapping("/api/tool/xmind")
@Tag(name = "XMind工具")
@CrossOrigin(origins = "*")
public class XmindController {

    @Autowired
    private XmindService xmindService;

    @PostMapping("/parse")
    @Operation(summary = "解析XMind文件并转换为测试用例")
    public Result<Map<String, Object>> parse(@RequestParam("file") MultipartFile file) throws IOException {
        if (file.isEmpty()) {
            return Result.error("文件不能为空");
        }
        String filename = file.getOriginalFilename();
        if (filename == null || !filename.endsWith(".xmind")) {
            return Result.error("只支持 .xmind 格式文件");
        }
        Map<String, Object> result = xmindService.parseXmind(file.getBytes());
        return Result.success(result);
    }
}
