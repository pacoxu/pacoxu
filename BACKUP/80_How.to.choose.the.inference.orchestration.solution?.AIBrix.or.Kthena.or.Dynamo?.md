# [How to choose the inference orchestration solution? AIBrix or Kthena or Dynamo?](https://github.com/pacoxu/pacoxu/issues/80)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2025-12-03T09:39:35+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2025/12/03/how-to-choose-the-inference-orchestration-solution-aibrix-or-kthena-or-dynamo/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2025-12-03`.
> Original URL: https://pacoxu.wordpress.com/2025/12/03/how-to-choose-the-inference-orchestration-solution-aibrix-or-kthena-or-dynamo/
<p><strong>Note: The content in this article is based on currently available public information and is intended for technical reference only. The effectiveness of each solution depends heavily on your specific workload, infrastructure, and ecosystem integration. The architectural affiliations and early design choices mentioned here do not determine their future direction. In practice, community activity, openness, and long-term evolution are often more important factors. Please evaluate and choose based on your own scenario.<br /></strong></p>

<h2>Introduction</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#introduction"></a></p>

<p>The landscape of open-source inference orchestration for Large Language Models (LLMs) has evolved rapidly in 2025. Multiple projects have emerged to address the challenges of deploying and scaling LLM inference workloads on Kubernetes, each with its own approach to workload management, resource orchestration, and performance optimization.</p>

<p>This blog post provides an overview of the current inference orchestration solutions, examines the convergence trends in the ecosystem, and raises important questions about when Prefill-Decode (PD) disaggregation truly provides value.</p>

<h2>The Current Landscape</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#the-current-landscape"></a></p>

<h3>Rapid Development, Gradual Convergence</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#rapid-development-gradual-convergence"></a></p>

<p>The inference orchestration space is characterized by:</p>

<ul>
<li><strong>Many implementations</strong>: Multiple projects solving similar problems</li>

<li><strong>Different architectural choices</strong>: Varying approaches to workload management</li>

<li><strong>Shared goals</strong>: All aim to optimize LLM inference at scale</li>

<li><strong>Emerging patterns</strong>: Common solutions beginning to emerge</li>
</ul>

<p>Despite the diversity, we&#8217;re seeing convergence around key patterns: LeaderWorkerSet (LWS)-based architectures, intelligent routing, and disaggregated serving models.</p>

<h2>Workload Orchestration Solutions</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#workload-orchestration-solutions"></a></p>

<h3>1. Dual LWS Architecture</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#1-dual-lws-architecture"></a></p>

<p><strong><a href="https://github.com/llm-d/llm-d">llm-d</a></strong>&nbsp;implements a dual LeaderWorkerSet architecture for Prefill-Decode disaggregation:</p>

<ul>
<li><strong>Two LWS instances</strong>: Separate LWS for prefill and decode workers</li>

<li><strong>KServe integration</strong>: Deep integration with KServe for model serving</li>

<li><strong>LMCache support</strong>: Efficient KV cache management across workers</li>

<li><strong>Routing sidecar</strong>: Intelligent request routing and cache optimization</li>
</ul>

<pre>
Client → Routing Sidecar → Prefill LWS → KV Cache → Decode LWS → Response

</pre>

<p><strong>Why dual LWS?</strong>&nbsp;This architecture enables independent scaling and resource optimization for each phase while maintaining coordination through the leader-worker pattern.</p>

<h3>2. Serving Group: Volcano Kthena</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#2-serving-group-volcano-kthena"></a></p>

<p><strong><a href="https://github.com/volcano-sh/kthena">Kthena</a></strong>&nbsp;takes a different approach with its&nbsp;<strong>Serving Group</strong>&nbsp;concept:</p>

<ul>
<li><strong>No dual LWS</strong>: Kthena intentionally avoids the dual LWS pattern</li>

<li><strong>Gang scheduling integration</strong>: Leverages Volcano&#8217;s gang scheduling capabilities</li>

<li><strong>Reduced layering</strong>: Eliminates the StatefulSet/Pod layer complexity</li>

<li><strong>Direct integration</strong>: Native integration with Volcano scheduler</li>
</ul>

<p><strong>Why not LWS?</strong>&nbsp;The Kthena team found that integrating with Volcano&#8217;s gang scheduling required a different architecture. The dual LWS, StatefulSet, and Pod layering added complexity without clear benefits for their use case.</p>

<p>This design choice reflects a key insight:&nbsp;<strong>the best orchestration solution depends on your existing infrastructure and scheduling requirements</strong>.</p>

<h3>3. StormService: AIBrix</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#3-stormservice-aibrix"></a></p>

<p><strong><a href="https://github.com/vllm-project/aibrix">AIBrix StormService</a></strong>&nbsp;provides specialized container lifecycle management for P/D disaggregation:</p>

<ul>
<li><strong>P/D lifecycle management</strong>: Fine-grained control over prefill and decode containers</li>

<li><strong>Multi-mode support</strong>: TP, PP, single GPU, and P/D disaggregation</li>

<li><strong>StormService and RoleSet CRDs</strong>: Custom resources for P/D orchestration</li>

<li><strong>Enterprise features</strong>: Multi-tenancy, routing, and observability</li>
</ul>

<p><strong>Architecture:</strong></p>

<pre>
AIBrix Control Plane
    ├── StormService Controller
    │   ├── RoleSet (Prefill)
    │   └── RoleSet (Decode)
    ├── Gateway &amp; Routing
    └── Autoscaler

</pre>

<h3>4. NVIDIA Dynamo: Two Modes</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#4-nvidia-dynamo-two-modes"></a></p>

<p><strong><a href="https://github.com/ai-dynamo/dynamo">Dynamo</a></strong>&nbsp;offers two distinct deployment modes:</p>

<p><strong>Grove Mode:</strong> <a href="https://github.com/ai-dynamo/dynamo/blob/be67f67b1a8d0837291ac7033af6edbc146f6995/docs/kubernetes/grove.md">https://github.com/ai-dynamo/dynamo/blob/be67f67b1a8d0837291ac7033af6edbc146f6995/docs/kubernetes/grove.md</a></p>

<ul>
<li>High-performance inference</li>

<li>NVIDIA-native deployment</li>

<li>Optimized for pure NVIDIA infrastructure
<ul>
<li>&#8220;GPU support depends on the engine: Dynamo uses backends vllm, sglang and trt-llm. Dynamo is the layer above that.&#8221; <a href="https://github.com/ai-dynamo/dynamo/issues/3604#issuecomment-3410989382">quota</a></li>
</ul>
</li>
</ul>

<p><strong>LWS Mode:</strong></p>

<ul>
<li>Kubernetes-native deployment using LeaderWorkerSet</li>

<li>Multi-node disaggregated serving</li>

<li>Integration with Kubernetes ecosystem</li>
</ul>

<p>This dual-mode approach allows users to choose the right level of abstraction for their infrastructure.</p>

<h3>5. SGLang RBG: LWS-Inspired</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#5-sglang-rbg-lws-inspired"></a></p>

<p><strong><a href="https://github.com/sgl-project/rbg">RBG (Resource-Aware Batch Scheduler)</a></strong>&nbsp;learned from and reused design patterns from LWS:</p>

<ul>
<li><strong>LWS-inspired</strong>: Incorporates proven patterns from LeaderWorkerSet</li>

<li><strong>Resource-aware scheduling</strong>: Optimizes batch scheduling based on resources</li>

<li><strong>Batch optimization</strong>: Intelligent batching strategies for throughput</li>

<li><strong>P/D support</strong>: Enables disaggregated prefill and decode workloads</li>
</ul>

<h2>Convergence Trends</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#convergence-trends"></a></p>

<h3>Common Patterns Emerging</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#common-patterns-emerging"></a></p>

<p>Despite different implementations, several patterns are converging:</p>

<table><thead><tr><th>Pattern</th><th>llm-d</th><th>Kthena</th><th>AIBrix</th><th>Dynamo</th><th>RBG</th></tr></thead><tbody><tr><td>LWS-based</td><td>✓ (dual)</td><td>✗</td><td>✗</td><td>✓ (option)</td><td>✓ (inspired)</td></tr><tr><td>P/D disaggregation</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td></tr><tr><td>Intelligent routing</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td></tr><tr><td>KV cache management</td><td>LMCache</td><td>Native</td><td>Distributed</td><td>Native</td><td>Native</td></tr></tbody></table>

<h3>Why So Many Implementations?</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#why-so-many-implementations"></a></p>

<p>The diversity reflects different optimization goals:</p>

<ol>
<li><strong>Scheduling integration</strong>: Kthena needs Volcano gang scheduling directly</li>

<li><strong>Enterprise features</strong>: AIBrix focuses on multi-tenancy and observability</li>

<li><strong>Performance focus</strong>: Dynamo optimizes for NVIDIA hardware</li>

<li><strong>Simplicity</strong>: RBG provides a lightweight LWS-inspired approach</li>

<li><strong>Production-readiness</strong>: llm-d demonstrates a complete reference implementation</li>
</ol>

<h2>The PD Disaggregation Question</h2>

<p>At <strong>KCD Hangzhou 2025</strong>, Wen Yuan Yu’s keynote <em>“Kubernetes Is Born for Service Resource Orchestration—MaaS Changes Everything”</em> raised an important question about <strong>PD-separation</strong>:</p>

<blockquote>
<p><em>“Achieving strong production gains from PD-separation is very difficult.<br />While stress testing can show great results, in real dynamic environments it becomes much harder.<br />Over-provisioning Decode introduces significant challenges.”</em></p>
</blockquote>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2025/12/image-5.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2025/12/image-5.png?w=1024" alt="" /></a>

<p>This observation directly challenges the assumption that <strong>PD-separation is always beneficial</strong>.<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#the-pd-disaggregation-question"></a></p>

<h3>Does PD Disaggregation Always Provide Value?<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#does-pd-disaggregation-always-provide-value"></a></h3>

<p>At&nbsp;<a href="https://www.bilibili.com/video/BV1dkUYBkEUc/">KCD Hangzhou 2025</a>, Yu Wen Yuan&#8217;s keynote &#8220;Kubernetes Was Built for Service-Resource Orchestration. MaaS Changes Everything&#8221; raised important questions about PD disaggregation:</p>

<blockquote>
<p>&#8220;PD-Disaggregate Role Scheduling • Not So Sure? (Our answer is Data Plane!)&#8221;</p>
</blockquote>

<p>This challenges the assumption that PD disaggregation is always beneficial.</p>

<h3>When PD Disaggregation Helps<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#when-pd-disaggregation-helps"></a></h3>

<p>PD disaggregation provides clear benefits when:</p>

<ul>
<li><strong>Long prefill, short decode</strong>: Input prompts are much longer than outputs</li>

<li><strong>High concurrency</strong>: Many simultaneous requests need serving</li>

<li><strong>Heterogeneous hardware</strong>: Different GPU types for different phases</li>

<li><strong>SLA-driven scheduling</strong>: Different latency requirements (TTFT vs TPOT)</li>
</ul>

<h3>When PD Disaggregation May Not Help</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#when-pd-disaggregation-may-not-help"></a></p>

<p>Consider alternatives when:</p>

<ul>
<li><strong>Short contexts</strong>: Both prefill and decode are fast</li>

<li><strong>Low concurrency</strong>: Few simultaneous requests</li>

<li><strong>Homogeneous hardware</strong>: Same GPUs for all workloads</li>

<li><strong>Complexity costs</strong>: Operational overhead outweighs benefits</li>

<li><strong>KV cache transfer overhead</strong>: Network latency exceeds computation savings</li>
</ul>

<h3>The Data Plane Perspective</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#the-data-plane-perspective"></a></p>

<p>The &#8220;Data Plane&#8221; answer suggests that the value of PD disaggregation depends on where bottlenecks actually exist. Before implementing complex orchestration:</p>

<ol>
<li><strong>Profile your workload</strong>: Understand where time is spent</li>

<li><strong>Measure KV cache transfer costs</strong>: Network overhead matters</li>

<li><strong>Consider simpler alternatives</strong>: TP/DP without disaggregation</li>

<li><strong>Evaluate operational complexity</strong>: More components = more failure modes</li>
</ol>

<h2>Configuration Optimization: AIConfigurator</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#configuration-optimization-aiconfigurator"></a></p>

<p>Choosing the right P/D configuration is complex. NVIDIA&#8217;s&nbsp;<strong><a href="https://github.com/ai-dynamo/aiconfigurator">AIConfigurator</a></strong>&nbsp;helps optimize disaggregated deployment configurations:</p>

<h3>What AIConfigurator Does</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#what-aiconfigurator-does"></a></p>

<ul>
<li><strong>Configuration space search</strong>: Evaluates thousands of P/D combinations</li>

<li><strong>SLA-constrained optimization</strong>: Finds configurations meeting TTFT/TPOT targets</li>

<li><strong>Hardware-specific tuning</strong>: Supports H100, H200, B200 with collected data</li>

<li><strong>xPyD planning</strong>: Determines optimal prefill/decode worker ratios</li>
</ul>

<h3>Example Usage</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#example-usage"></a></p>

<pre># Find optimal configuration for Qwen3-32B on 32 H200 GPUs
# with SLA targets: TTFT ≤ 300ms, TPOT ≤ 10ms
aiconfigurator cli default \
  --model QWEN3_32B \
  --total_gpus 32 \
  --system h200_sxm \
  --isl 4000 \
  --osl 500 \
  --ttft 300 \
  --tpot 10</pre>

<h3>Why AIConfigurator Matters</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#why-aiconfigurator-matters"></a></p>

<p>Traditional autoscaling (HPA/KPA) doesn&#8217;t understand LLM-specific characteristics. AIConfigurator provides:</p>

<ul>
<li><strong>Informed decisions</strong>: Data-driven configuration choices</li>

<li><strong>Predictive optimization</strong>: Estimate performance before deployment</li>

<li><strong>Resource efficiency</strong>: Maximize GPU utilization with SLA guarantees</li>
</ul>

<h2>Recommendations</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#recommendations"></a></p>

<h3>For New Deployments</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#for-new-deployments"></a></p>

<ol>
<li><strong>Start simple</strong>: Begin with monolithic serving (no P/D disaggregation)</li>

<li><strong>Profile first</strong>: Understand your workload characteristics</li>

<li><strong>Use AIConfigurator</strong>: Let data guide configuration decisions</li>

<li><strong>Add complexity gradually</strong>: Introduce P/D only when benefits are clear</li>
</ol>

<h3>For Existing Infrastructure</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#for-existing-infrastructure"></a></p>

<table><thead><tr><th>If you use&#8230;</th><th>Consider&#8230;</th></tr></thead><tbody><tr><td>Volcano</td><td>Kthena (native integration)</td></tr><tr><td>KServe</td><td>llm-d (deep integration)</td></tr><tr><td>vLLM</td><td>AIBrix (vLLM ecosystem)</td></tr><tr><td>NVIDIA GPUs</td><td>Dynamo (NVIDIA optimization)</td></tr><tr><td>SGLang</td><td>RBG (LWS-inspired, lightweight)</td></tr></tbody></table>

<h3>Key Questions Before Adopting PD Disaggregation</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#key-questions-before-adopting-pd-disaggregation"></a></p>

<ol>
<li><strong>Is your prefill time &gt;&gt; decode time?</strong>&nbsp;If not, disaggregation may not help.</li>

<li><strong>Can your network handle KV cache transfer?</strong>&nbsp;Network overhead can eliminate gains.</li>

<li><strong>Do you need independent scaling?</strong>&nbsp;If P and D scale together, keep them together.</li>

<li><strong>Is operational complexity acceptable?</strong>&nbsp;More components = more failure modes.</li>
</ol>

<h2>Conclusion</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#conclusion"></a></p>

<p>The inference orchestration landscape is diverse but converging. Key takeaways:</p>

<ul>
<li><strong>Multiple solutions exist</strong>&nbsp;because different infrastructure has different needs</li>

<li><strong>LWS-based patterns are popular</strong>&nbsp;but not universal (Kthena&#8217;s Serving Group shows alternatives)</li>

<li><strong>PD disaggregation is not always valuable</strong>&nbsp;&#8211; profile your workload first</li>

<li><strong>Tools like AIConfigurator help</strong>&nbsp;navigate the complex configuration space</li>

<li><strong>Start simple, add complexity when needed</strong>&nbsp;based on actual measurements</li>
</ul>

<p>The future will likely see further consolidation around proven patterns, but the current diversity reflects healthy experimentation in a rapidly evolving field.</p>

<hr />

<h2>References</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#references"></a></p>

<h3>Workload Orchestration Projects</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#workload-orchestration-projects"></a></p>

<ul>
<li><a href="https://github.com/llm-d/llm-d">llm-d</a>&nbsp;&#8211; Dual LWS architecture for P/D</li>

<li><a href="https://github.com/volcano-sh/kthena">Kthena</a>&nbsp;&#8211; Volcano-based Serving Group</li>

<li><a href="https://github.com/vllm-project/aibrix">AIBrix</a>&nbsp;&#8211; StormService for P/D</li>

<li><a href="https://github.com/ai-dynamo/dynamo">Dynamo</a>&nbsp;&#8211; NVIDIA inference platform</li>

<li><a href="https://github.com/sgl-project/rbg">RBG</a>&nbsp;&#8211; LWS-inspired batch scheduler</li>
</ul>

<h3>Configuration Tools</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#configuration-tools"></a></p>

<ul>
<li><a href="https://github.com/ai-dynamo/aiconfigurator">AIConfigurator</a>&nbsp;&#8211; P/D configuration optimizer</li>
</ul>

<h3>Related Documentation</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#related-documentation"></a></p>

<ul>
<li><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/inference/pd-disaggregation.md">PD Disaggregation Overview</a></li>

<li><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/inference/README.md">Inference Guide</a></li>

<li><a href="https://github.com/kubernetes-sigs/lws">LWS (LeaderWorkerSet)</a></li>
</ul>

<h3>Presentations</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-12-01/inference-orchestration.md#presentations"></a></p>

<ul>
<li><a href="https://www.bilibili.com/video/BV1dkUYBkEUc/">KCD China 2025: Kubernetes Was Built for Service-Resource Orchestration. MaaS Changes Everything</a></li>

<li><a href="https://github.com/user-attachments/files/23845814/04-kubernetes-was-built-for-service-resource-orchestration.-maas-changes-everything-yu-wen-yuan-.pdf">PDF Slides</a></li>
</ul>

<p></p>
