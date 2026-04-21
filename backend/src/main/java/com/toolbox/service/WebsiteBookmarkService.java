package com.toolbox.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.toolbox.entity.WebsiteBookmark;
import com.toolbox.mapper.WebsiteBookmarkMapper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class WebsiteBookmarkService extends ServiceImpl<WebsiteBookmarkMapper, WebsiteBookmark> {

    public List<WebsiteBookmark> getAllBookmarks() {
        LambdaQueryWrapper<WebsiteBookmark> wrapper = new LambdaQueryWrapper<>();
        wrapper.orderByDesc(WebsiteBookmark::getCreateTime);
        return this.list(wrapper);
    }

    public boolean addBookmark(WebsiteBookmark bookmark) {
        return this.save(bookmark);
    }

    public boolean updateBookmark(WebsiteBookmark bookmark) {
        return this.updateById(bookmark);
    }

    public boolean deleteBookmark(Long id) {
        return this.removeById(id);
    }

    public List<WebsiteBookmark> searchBookmarks(String keyword) {
        LambdaQueryWrapper<WebsiteBookmark> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(WebsiteBookmark::getName, keyword)
                .or().like(WebsiteBookmark::getUrl, keyword)
                .or().like(WebsiteBookmark::getDescription, keyword);
        wrapper.orderByDesc(WebsiteBookmark::getCreateTime);
        return this.list(wrapper);
    }
}
