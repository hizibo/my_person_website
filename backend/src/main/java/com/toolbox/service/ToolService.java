package com.toolbox.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.toolbox.entity.Tool;
import com.toolbox.mapper.ToolMapper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ToolService extends ServiceImpl<ToolMapper, Tool> {

    public List<Tool> getOnlineTools() {
        LambdaQueryWrapper<Tool> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Tool::getStatus, "online").orderByAsc(Tool::getSort);
        return this.list(wrapper);
    }

    public List<Tool> getAllTools() {
        return this.list(new LambdaQueryWrapper<>());
    }

    public boolean addTool(Tool tool) {
        return this.save(tool);
    }

    public boolean updateTool(Tool tool) {
        return this.updateById(tool);
    }
}
