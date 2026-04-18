package com.toolbox;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.EnableAspectJAutoProxy;

@SpringBootApplication
@MapperScan("com.toolbox.mapper")
@EnableAspectJAutoProxy
public class ToolboxApplication {

    public static void main(String[] args) {
        SpringApplication.run(ToolboxApplication.class, args);
    }
}
