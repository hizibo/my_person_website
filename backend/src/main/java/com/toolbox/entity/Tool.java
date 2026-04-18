package com.toolbox.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("sys_tool")
public class Tool {
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String toolId;       // 工具唯一标识，如 xmind2case
    private String name;          // 工具名称
    private String icon;          // 图标 emoji
    private String category;      // 分类
    private String description;   // 描述
    private String route;         // 前端路由
    private String backendPath;   // 后端接口路径
    private String status;        // online | offline | dev
    private Integer sort;         // 排序
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
