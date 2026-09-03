"""
== 注意（2026-09-02）==
本脚本的题库部分（QUESTIONS）已迁移至 data/questions/architecture-questions.json，
自产题的唯一权威源现在是 data/ 下的 JSON。填空题/案例/论文请改用：
    tools/python/python.exe data/import_materials.py
本文件只保留【知识树 + 关系】两类数据，作为快速初始化之用；若以 data/ 管道为准，
知识树也用 data/syllabus/architecture-syllabus.json 中的完整 136 节点导入，
不需要这里精简版 KNOWLEDGE 兜底。二者通过 code 去重，可安全共存。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from app.database import SessionLocal
from app.models.knowledge import KnowledgePoint, KnowledgeRelation

# (parent_code or None, code, name, description, subject)
KNOWLEDGE = [
    ("1", "1.1", "计算机组成与体系结构", "CPU/存储/总线/指令系统/流水线/多核", 1),
    ("1", "1.2", "操作系统", "进程线程/调度/死锁/存储管理/文件系统", 1),
    ("1", "1.3", "数据库系统", "ER模型/范式/事务ACID/并发控制/索引/分布式数据库", 1),
    ("1", "1.4", "计算机网络", "OSI/TCP-IP/网络设备/路由/云网络", 1),
    ("2", "2.1", "软件过程与生命周期", "瀑布/迭代/敏捷/DevOps", 1),
    ("2", "2.2", "需求工程", "需求获取/分析/规格说明/验证", 1),
    ("2", "2.3", "软件设计", "结构化/面向对象/UML/设计模式", 1),
    ("2", "2.4", "软件测试与质量", "测试层次/用例设计/质量模型ISO25010", 1),
    ("2", "2.5", "项目管理", "范围/进度/成本/风险/挣值管理", 1),
    ("2", "2.6", "配置管理", "版本/变更/基线", 1),
    ("3", "3.7", "中间件技术", "消息中间件/事务中间件/应用服务器/对象中间件", 1),
    ("3", "3.8", "大数据架构", "Hadoop/Spark/数据湖/流式计算/Lambda架构", 1),
    ("3", "3.9", "物联网与边缘计算", "感知层/网络层/平台层/边缘计算", 1),
    ("3", "3.10", "人工智能与智能系统", "机器学习/深度学习/知识图谱/智能体", 1),
    ("4", "4.1", "运筹学基础", "线性规划/动态规划/网络计划", 1),
    ("4", "4.2", "概率统计", "概率分布/期望/方差/贝叶斯", 1),
    ("4", "4.3", "算法与复杂度", "复杂度分析/常用算法/数据结构", 1),
    ("5", "5.1", "网络安全技术", "加密/认证/访问控制/防火墙/等保", 1),
    ("5", "5.2", "系统可靠性设计", "可靠性模型/冗余/容错/RAID/可用性计算", 1),
    ("3.1", "3.1.1", "管道-过滤器与数据流风格", "构件间以数据流连接", 1),
    ("3.1", "3.1.2", "仓库风格与黑板系统", "以共享数据为中心", 1),
    ("3.1", "3.1.3", "分层与调用-返回风格", "层间接口调用", 1),
    ("3.1", "3.1.4", "事件驱动与微内核风格", "事件发布订阅/最小内核", 1),
    ("3.2", "3.2.1", "性能与可用性", "响应时间/吞吐量/故障恢复", 1),
    ("3.2", "3.2.2", "安全性与可修改性", "机密性/完整性/可维护", 1),
    ("3.2", "3.2.3", "质量属性场景", "刺激-环境-响应六要素", 1),
    ("3.4", "3.4.1", "服务发现与注册中心", "Nacos/Eureka/Consul", 1),
    ("3.4", "3.4.2", "API 网关与流量治理", "路由/限流/熔断/灰度", 1),
    ("3.4", "3.4.3", "分布式事务与最终一致性", "TCC/Saga/消息事务", 1),
    ("3.4", "3.4.4", "容器化与部署", "Docker/K8s/CI-CD", 1),
    ("1.3", "1.3.1", "关系模型与范式", "1NF-3NF-BCNF/ER", 1),
    ("1.3", "1.3.2", "事务与并发控制", "ACID/隔离级别/锁", 1),
    ("1.3", "1.3.3", "索引与查询优化", "B+树/执行计划", 1),
    ("1.3", "1.3.4", "分布式数据库", "分库分表/一致性协议", 1),
    ("1.4", "1.4.1", "TCP/IP 协议族", "TCP/UDP/HTTP/DNS", 1),
    ("1.4", "1.4.2", "路由与交换", "路由协议/VLAN", 1),
    ("1.4", "1.4.3", "负载均衡与 CDN", "LVS/Nginx/边缘缓存", 1),
    ("5.1", "5.1.1", "密码学基础", "对称/非对称/哈希", 1),
    ("5.1", "5.1.2", "认证与访问控制", "数字签名/权限模型", 1),
    ("5.1", "5.1.3", "等保与安全合规", "等级保护/合规要求", 1),
    ("2.3", "2.3.1", "UML 建模", "用例图/类图/序列图", 1),
    ("2.3", "2.3.2", "设计模式", "创建/结构/行为型", 1),
    ("2.3", "2.3.3", "面向对象设计原则", "SOLID/开闭原则", 1),
]

# (from_code, to_code, relation_type)
RELATIONS = [
    ("2", "3", "prerequisite"),
    ("2.2", "2.3", "prerequisite"),
    ("2.3", "3.1", "prerequisite"),
    ("1.2", "1.3", "prerequisite"),
    ("1.4", "5.1", "prerequisite"),
    ("3.1", "3.2", "related"),
    ("3.2", "3.4", "related"),
    ("3.3", "3.4", "related"),
    ("3.5", "3.6", "related"),
    ("1.3", "3.8", "related"),
    ("1.4", "3.9", "related"),
    ("3.8", "3.6", "related"),
    ("5.2", "3", "related"),
    ("4.1", "2.5", "related"),
    ("3.2.3", "3.3", "related"),
    ("3.4.3", "1.3.2", "related"),
    ("1.4.3", "3.2.1", "related"),
    ("2.3.2", "3.1.4", "related"),
    ("3.4.4", "3.6", "related"),
    ("5.1.1", "5.1.2", "prerequisite"),
]


def main():
    db = SessionLocal()
    code2id = {k.code: k.id for k in db.query(KnowledgePoint).all()}
    added_kp = 0
    for parent_code, code, name, desc, subject in KNOWLEDGE:
        if code in code2id:
            continue
        parent_id = code2id.get(parent_code)
        kp = KnowledgePoint(parent_id=parent_id, code=code, name=name, description=desc, subject=subject)
        db.add(kp)
        db.flush()
        code2id[code] = kp.id
        added_kp += 1
    db.commit()
    print("knowledge points added:", added_kp, "total:", len(code2id))

    added_rel = 0
    for fc, tc, rt in RELATIONS:
        f, t = code2id.get(fc), code2id.get(tc)
        if not f or not t:
            print("skip relation", fc, tc)
            continue
        dup = db.query(KnowledgeRelation).filter_by(from_id=f, to_id=t, relation_type=rt).first()
        if dup:
            continue
        db.add(KnowledgeRelation(from_id=f, to_id=t, relation_type=rt))
        added_rel += 1
    db.commit()
    print("relations added:", added_rel)

    db.close()

if __name__ == "__main__":
    main()
