#!/bin/bash
# Jenkins 启动脚本（优化内存配置）
# 日期: 2026-05-13
# 功能: 使用优化配置启动 Jenkins 容器
# 内存: 1G 容器内存 + 700M JVM 堆 + G1GC 垃圾收集器

docker run -d \
  --name jenkins \
  --restart unless-stopped \
  -p 8088:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /opt/my-toolbox:/opt/my-toolbox \
  -v /usr/bin/docker:/usr/bin/docker \
  -m 1g \
  --memory-swap 2g \
  -e JAVA_OPTS='-Xmx700m -Xms256m -XX:MaxRAMPercentage=75.0 -XX:+UseG1GC -XX:+UseContainerSupport' \
  jenkins/jenkins:lts