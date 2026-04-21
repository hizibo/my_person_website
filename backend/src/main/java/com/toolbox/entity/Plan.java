package com.toolbox.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("plan")
public class Plan {
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String title;          // 计划标题
    private String description;    // 计划描述
    private Integer progress;      // 进度(0-100)
    private String status;         // 状态: active/completed/cancelled
    private Integer sort;         // 排序（正序，小的在前）
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}