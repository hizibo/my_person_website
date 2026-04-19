package com.toolbox.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.toolbox.entity.Plan;
import com.toolbox.mapper.PlanMapper;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class PlanService extends ServiceImpl<PlanMapper, Plan> {

    public List<Plan> getAllPlans() {
        LambdaQueryWrapper<Plan> wrapper = new LambdaQueryWrapper<>();
        wrapper.orderByDesc(Plan::getCreateTime);
        return this.list(wrapper);
    }

    public boolean addPlan(Plan plan) {
        return this.save(plan);
    }

    public boolean updatePlan(Plan plan) {
        return this.updateById(plan);
    }

    public boolean deletePlan(Long id) {
        return this.removeById(id);
    }
}