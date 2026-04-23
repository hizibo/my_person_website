package com.toolbox.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("note_category")
public class NoteCategory {
    @TableId(type = IdType.AUTO)
    private Long id;

    private String name;          // 分类名称
    private Long parentId;        // 父分类ID，0表示根分类
    private Integer sort;         // 排序
    private LocalDateTime createTime;
    private LocalDateTime updateTime;

    @TableField(exist = false)
    private Integer noteCount;    // 该分类下的笔记数量（含子分类）
}
