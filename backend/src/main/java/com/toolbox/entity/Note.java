package com.toolbox.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("note")
public class Note {
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long categoryId;      // 分类ID
    private String title;         // 笔记标题
    private String content;       // 笔记内容（HTML格式）
    private String summary;       // 摘要
    private String tags;          // 标签，逗号分隔
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}