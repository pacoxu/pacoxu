# [KubeCon 现场见闻：从 HeadLamp 到 MCP 热潮](https://github.com/pacoxu/pacoxu/issues/73)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2025-04-11T18:48:08+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2025/04/11/kubecon-%e7%8e%b0%e5%9c%ba%e8%a7%81%e9%97%bb%ef%bc%9a%e4%bb%8e-headlamp-%e5%88%b0-mcp-%e7%83%ad%e6%bd%ae/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2025-04-11`.
> Original URL: https://pacoxu.wordpress.com/2025/04/11/kubecon-%e7%8e%b0%e5%9c%ba%e8%a7%81%e9%97%bb%ef%bc%9a%e4%bb%8e-headlamp-%e5%88%b0-mcp-%e7%83%ad%e6%bd%ae/
<p>本次大会上，不仅有各类技术项目的精彩展示，还有不少轻量级工具与社区项目引起了广泛关注。以下是我对部分亮点的整理与感受。</p>

<h2><strong>HeadLamp</strong> </h2>

<p>作为 Kubernetes 社区项目，正以极具竞争力的姿态亮相。</p>

<ul>
<li><strong>替代方案优势</strong>：HeadLamp 的功能已经足够丰富，可以取代传统的 kube dashboard 以及 KubeSphere部分功能。</li>

<li><strong>微软风格的桌面体验</strong>：Keynote 演示中，微软展现了将其打造为每个 Kubernetes 用户的必备桌面应用的意图。与 Lens 等竞品相比，其轻量、便捷、支持自部署的特点给人留下深刻印象——用户只需将各个集群的 token 或证书添加进来，即可快速上手管理。</li>
</ul>

<h2>ETCD Operator</h2>

<p><strong>关注热度与现状</strong>：项目启动之初吸引了不少关注，但目前实际参与者非常少，正处于 “help wanted” 阶段。</p>

<h2>跨领域协作与挑战</h2>

<p><strong>弹性指标定义挑战</strong>：在 LLM 场景下如何定义弹性指标仍是一大难题</p>

<p>当前对 s3 modeling 的支持让人颇感无奈，这些都为社区未来的设计改善留下了想象空间。</p>

<p>推理领域： vllm production stack、KServer 、AIBrix 、 llmaz  的对比，目前感受上 KServe 有很多历史包袱，迫于之前用户和产品的要求很难直接做颠覆性重构，这也带来了一种担忧。AIBrix 和 llmaz 都是刚刚起步，AIBrix 有字节背书；llmaz 的目标则是更轻量。</p>

<h2>MCP 热潮 —— 新项目与支持的风起云涌</h2>

<p>本周又见一波 MCP 热潮：</p>

<p>另外，clusterpedia 的也需要相关方案，由 manusa 和 silenceper 推出的 kube MCP 项目也在积极探索中。</p>

<p><strong>项目多元化</strong>：不少新建热门项目纷纷加入 MCP 支持行列，有项目直接在已有项目中添加 MCP 支持。</p>

<p><strong>实例展示</strong>：</p>

<p><a href="https://github.com/dagger/dagger/pull/9935">dagger 与 MCP 的整合</a></p>

<p><a href="https://github.com/k8sgpt-ai/k8sgpt/issues/1392">k8sgpt 的 MCP 讨论</a></p>

<h2>Steering 年报与 SIG 动态</h2>

<p>一些需要更贡献者参与的点， Steering 团队基于各个 SIG/WG 的年报进行了总结：<strong>需要帮助的项目</strong>：各 SIG 维护者在年报中均提到若干待解项目和功能点，展现了社区在持续迭代和改进中的求助信号。</p>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2025/04/image.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2025/04/image.png?w=1024" alt="" /></a>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2025/04/image-1.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2025/04/image-1.png?w=1024" alt="" /></a>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2025/04/image-2.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2025/04/image-2.png?w=1024" alt="" /></a>

<h2>展台与 Demo Theater 的亮点</h2>

<p><strong>现场展区</strong>同样吸引了众多关注：</p>

<ul>
<li><strong>Wiz 展台</strong>：展示了丰富的安全工具 UI，从演示中可以感受到其在安全领域的坚实基础。</li>

<li><strong>Demo Theater</strong>：不少 sponsor 的演示项目大放异彩，如 Google 现场展示的 65k node 演示给与会者留下了深刻印象。</li>

<li><strong>热门展区主题</strong>：当前最受欢迎的包括可观测性、安全、AI + Gateway 等方向，另有 Kubeflow 专题也成为亮点之一。</li>
</ul>

<h2>会场全景与个人感受</h2>

<p>在现场的诸多体验中，也有一些值得一提的地方：</p>

<ul>
<li><strong>行程安排的小插曲</strong>：第一天一早到达时状态不佳，参加 Maintainer Summit 时主要参与了 Steering 的 AMA。同时，预定的民宿体验不如预期，提示大家尽量避免使用 Booking.com 订房。</li>

<li><strong>最佳 End User 奖项</strong>：来自海外的 KubeCon 首次将此奖项授予中国企业蚂蚁集团，此前国内的京东和滴滴曾获得该奖，但是实在 KubeCon China。评判标准更多聚焦在社区贡献上。</li>

<li><strong>国际视野</strong>：日本专场圆桌中可见维护者数量和议题均有所增加。</li>

<li>End User: 欧洲 KubeCon 的 End User 演讲更是覆盖了从工业到农业的各个领域。</li>

<li><strong>会议场地设计</strong>：此次会场的房间布局略显“奇特”——Room A-H 人气颇旺，而部分在三楼或隐蔽位置（如 ROOM IJ）的场地则稍显冷清。</li>

<li><strong>演讲大会回顾</strong>：
<ul>
<li><strong>热门主题</strong>：AI 相关议题（如 LLM、Ollama、Benchmark、DRA、k8sgpt）备受关注；此外，Argo、Cilium、Otel 与 Platform Engineering 也都有不少观众。</li>

<li><strong>项目展示</strong>：Project Lighting 场次人气高涨；而在其他项目中，keynote 中呈现的 honeycomb 效果不错，karpenter、cluster-api 与 vCluster（我的主题）等均引发了会后踊跃讨论。</li>

<li><strong>部分领域的冷场</strong>：部分偏维护者或底层技术的主题，如存储，本次的参与度和热度相对较低。</li>
</ul>
</li>

<li><strong>餐饮体验</strong>：与过去相比，现场的用餐体验似乎又回到了曾经的“难吃”状态（巴黎好像饮食非常棒），主要是冷。</li>
</ul>

<p>本次活动超过12500人参加，是史上新高，云原生的热潮似乎并没有冷却，加油👍</p>
