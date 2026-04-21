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
        wrapper.orderByAsc(Plan::getSort);
        return this.list(wrapper);
    }

    public boolean addPlan(Plan plan) {
        // 新增时 sort 默认取当前最大 sort + 1（sort=0 或 null 时走默认逻辑）
        if (plan.getSort() == null || plan.getSort() == 0) {
            List<Object> objs = this.baseMapper.selectObjs(
                new LambdaQueryWrapper<Plan>().select(Plan::getSort).orderByDesc(Plan::getSort).last("LIMIT 1")
            );
            int maxSort = objs != null && !objs.isEmpty() && objs.get(0) != null ? ((Number) objs.get(0)).intValue() : 0;
            plan.setSort(maxSort + 1);
        }
        return this.save(plan);
    }

    public boolean updatePlan(Plan plan) {
        return this.updateById(plan);
    }

    public boolean deletePlan(Long id) {
        return this.removeById(id);
    }

    public List<Plan> searchPlans(String keyword) {
        LambdaQueryWrapper<Plan> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(Plan::getTitle, keyword).or().like(Plan::getDescription, keyword);
        wrapper.orderByAsc(Plan::getSort);
        return this.list(wrapper);
    }
}