package com.toolbox.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.toolbox.entity.Tool;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface ToolMapper extends BaseMapper<Tool> {
}
