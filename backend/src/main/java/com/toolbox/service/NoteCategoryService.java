package com.toolbox.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.toolbox.entity.Note;
import com.toolbox.entity.NoteCategory;
import com.toolbox.mapper.NoteCategoryMapper;
import com.toolbox.mapper.NoteMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class NoteCategoryService extends ServiceImpl<NoteCategoryMapper, NoteCategory> {

    @Autowired
    private NoteMapper noteMapper;

    /**
     * 获取所有分类（按父级ID和排序），带笔记数量
     */
    public List<NoteCategory> getAllCategories() {
        LambdaQueryWrapper<NoteCategory> wrapper = new LambdaQueryWrapper<>();
        wrapper.orderByAsc(NoteCategory::getParentId, NoteCategory::getSort);
        List<NoteCategory> categories = this.list(wrapper);
        populateNoteCount(categories);
        return categories;
    }

    /**
     * 获取根分类（parentId = 0），带笔记数量
     */
    public List<NoteCategory> getRootCategories() {
        LambdaQueryWrapper<NoteCategory> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NoteCategory::getParentId, 0).orderByAsc(NoteCategory::getSort);
        List<NoteCategory> categories = this.list(wrapper);
        populateNoteCount(categories);
        return categories;
    }

    /**
     * 根据父级ID获取子分类，带笔记数量
     */
    public List<NoteCategory> getChildrenCategories(Long parentId) {
        LambdaQueryWrapper<NoteCategory> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NoteCategory::getParentId, parentId).orderByAsc(NoteCategory::getSort);
        List<NoteCategory> categories = this.list(wrapper);
        populateNoteCount(categories);
        return categories;
    }

    /**
     * 填充每个分类的直接笔记数量
     */
    private void populateNoteCount(List<NoteCategory> categories) {
        if (categories == null || categories.isEmpty()) return;

        // 为每个分类查询笔记数量
        for (NoteCategory cat : categories) {
            Long count = noteMapper.selectCount(
                    new LambdaQueryWrapper<Note>()
                            .eq(Note::getCategoryId, cat.getId())
            );
            cat.setNoteCount(count.intValue());
        }
    }

    /**
     * 添加分类
     */
    public boolean addCategory(NoteCategory category) {
        return this.save(category);
    }

    /**
     * 更新分类
     */
    public boolean updateCategory(NoteCategory category) {
        return this.updateById(category);
    }

    /**
     * 删除分类（需要检查是否有子分类或笔记）
     */
    public boolean deleteCategory(Long id) {
        // 检查是否有子分类
        Long childCount = this.lambdaQuery().eq(NoteCategory::getParentId, id).count();
        if (childCount > 0) {
            return false; // 存在子分类，不能删除
        }
        // TODO: 检查是否有笔记属于该分类
        return this.removeById(id);
    }

    /**
     * 获取指定分类及其所有子分类的ID列表
     */
    public List<Long> getCategoryAndAllChildrenIds(Long categoryId) {
        List<Long> ids = new java.util.ArrayList<>();
        ids.add(categoryId);
        collectChildrenIds(categoryId, ids);
        return ids;
    }

    /**
     * 递归收集所有子分类ID
     */
    private void collectChildrenIds(Long parentId, List<Long> ids) {
        List<NoteCategory> children = this.lambdaQuery()
                .eq(NoteCategory::getParentId, parentId)
                .list();
        for (NoteCategory child : children) {
            ids.add(child.getId());
            collectChildrenIds(child.getId(), ids);
        }
    }}
