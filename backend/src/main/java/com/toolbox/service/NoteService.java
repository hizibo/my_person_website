package com.toolbox.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.toolbox.common.PageResult;
import com.toolbox.entity.Note;
import com.toolbox.mapper.NoteMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class NoteService extends ServiceImpl<NoteMapper, Note> {

    @Autowired
    private NoteCategoryService noteCategoryService;

    /**
     * 获取所有笔记（按修改时间倒序，分页）
     */
    public PageResult<Note> getAllNotes(Integer pageNum, Integer pageSize) {
        Page<Note> page = new Page<>(pageNum, pageSize);
        LambdaQueryWrapper<Note> wrapper = new LambdaQueryWrapper<>();
        wrapper.orderByDesc(Note::getUpdateTime);
        Page<Note> result = this.page(page, wrapper);
        return new PageResult<>(result);
    }

    /**
     * 根据分类ID获取笔记（仅当前分类，不含子分类，分页）
     */
    public PageResult<Note> getNotesByCategoryId(Long categoryId, Integer pageNum, Integer pageSize) {
        Page<Note> page = new Page<>(pageNum, pageSize);
        LambdaQueryWrapper<Note> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Note::getCategoryId, categoryId).orderByDesc(Note::getUpdateTime);
        Page<Note> result = this.page(page, wrapper);
        return new PageResult<>(result);
    }

    /**
     * 根据分类ID获取笔记（含子分类，分页）
     */
    public PageResult<Note> getNotesByCategoryIdWithChildren(Long categoryId, Integer pageNum, Integer pageSize) {
        List<Long> categoryIds = noteCategoryService.getCategoryAndAllChildrenIds(categoryId);
        Page<Note> page = new Page<>(pageNum, pageSize);
        LambdaQueryWrapper<Note> wrapper = new LambdaQueryWrapper<>();
        wrapper.in(Note::getCategoryId, categoryIds).orderByDesc(Note::getUpdateTime);
        Page<Note> result = this.page(page, wrapper);
        return new PageResult<>(result);
    }

    /**
     * 搜索笔记（标题或内容模糊匹配，分页）
     */
    public PageResult<Note> searchNotes(String keyword, Integer pageNum, Integer pageSize) {
        Page<Note> page = new Page<>(pageNum, pageSize);
        LambdaQueryWrapper<Note> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(Note::getTitle, keyword).or().like(Note::getContent, keyword);
        wrapper.orderByDesc(Note::getCreateTime);
        Page<Note> result = this.page(page, wrapper);
        return new PageResult<>(result);
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
