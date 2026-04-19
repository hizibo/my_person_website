package com.toolbox.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.toolbox.entity.NoteCategory;
import com.toolbox.mapper.NoteCategoryMapper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class NoteCategoryService extends ServiceImpl<NoteCategoryMapper, NoteCategory> {

    /**
     * 获取所有分类（按父级ID和排序）
     */
    public List<NoteCategory> getAllCategories() {
        LambdaQueryWrapper<NoteCategory> wrapper = new LambdaQueryWrapper<>();
        wrapper.orderByAsc(NoteCategory::getParentId, NoteCategory::getSort);
        return this.list(wrapper);
    }

    /**
     * 获取根分类（parentId = 0）
     */
    public List<NoteCategory> getRootCategories() {
        LambdaQueryWrapper<NoteCategory> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NoteCategory::getParentId, 0).orderByAsc(NoteCategory::getSort);
        return this.list(wrapper);
    }

    /**
     * 根据父级ID获取子分类
     */
    public List<NoteCategory> getChildrenCategories(Long parentId) {
        LambdaQueryWrapper<NoteCategory> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NoteCategory::getParentId, parentId).orderByAsc(NoteCategory::getSort);
        return this.list(wrapper);
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
}