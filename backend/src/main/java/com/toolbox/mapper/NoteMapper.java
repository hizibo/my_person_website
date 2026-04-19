package com.toolbox.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.toolbox.entity.Note;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface NoteMapper extends BaseMapper<Note> {
}