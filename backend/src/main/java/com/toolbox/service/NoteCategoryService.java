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
import java.util.Map;
import java.util.stream.Collectors;

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

        List<Long> allIds = categories.stream()
                .map(NoteCategory::getId)
                .collect(Collectors.toList());

        // 一次性查询所有分类的笔记数量
        List<Map<String, Object>> countResults = noteMapper.selectMaps(
                new LambdaQueryWrapper<Note>()
                        .select(com.baomidou.mybatisplus.core.toolkit.Constants.COUNT, "categoryId")
                        .in(Note::getCategoryId, allIds)
                        .groupBy(Note::getCategoryId)
        );

        Map<Long, Integer> countMap = countResults.stream()
                .collect(Collectors.toMap(
                        row -> ((Number) row.get("categoryId")).longValue(),
                        row -> ((Number) row.get("COUNT(*)")).intValue()
                ));

        for (NoteCategory cat : categories) {
            cat.setNoteCount(countMap.getOrDefault(cat.getId(), 0));
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
}
