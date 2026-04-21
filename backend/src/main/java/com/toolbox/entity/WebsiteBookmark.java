package com.toolbox.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("website_bookmark")
public class WebsiteBookmark {
    @TableId(type = IdType.AUTO)
    private Long id;

    private String name;          // 网站名称
    private String url;           // 网站地址
    private String account;       // 账号（非必填）
    private String password;      // 密码（非必填）
    private String description;   // 网站描述
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
