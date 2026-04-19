package com.toolbox.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.toolbox.entity.NoteCategory;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface NoteCategoryMapper extends BaseMapper<NoteCategory> {
}