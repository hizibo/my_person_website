package com.toolbox.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.toolbox.entity.Note;
import com.toolbox.mapper.NoteMapper;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class NoteService extends ServiceImpl<NoteMapper, Note> {

    /**
     * 获取所有笔记（按创建时间倒序）
     */
    public List<Note> getAllNotes() {
        LambdaQueryWrapper<Note> wrapper = new LambdaQueryWrapper<>();
        wrapper.orderByDesc(Note::getCreateTime);
        return this.list(wrapper);
    }

    /**
     * 根据分类ID获取笔记
     */
    public List<Note> getNotesByCategoryId(Long categoryId) {
        LambdaQueryWrapper<Note> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Note::getCategoryId, categoryId).orderByDesc(Note::getCreateTime);
        return this.list(wrapper);
    }

    /**
     * 搜索笔记（标题或内容模糊匹配）
     */
    public List<Note> searchNotes(String keyword) {
        LambdaQueryWrapper<Note> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(Note::getTitle, keyword).or().like(Note::getContent, keyword);
        wrapper.orderByDesc(Note::getCreateTime);
        return this.list(wrapper);
    }

    /**
     * 添加笔记
     */
    public boolean addNote(Note note) {
        return this.save(note);
    }

    /**
     * 更新笔记
     */
    public boolean updateNote(Note note) {
        return this.updateById(note);
    }

    /**
     * 删除笔记
     */
    public boolean deleteNote(Long id) {
        return this.removeById(id);
    }

    /**
     * 根据ID获取笔记详情
     */
    public Note getNoteById(Long id) {
        return this.getById(id);
    }
}