# [Kubernetes Introduces Native Gang Scheduling Support to Better Serve AI/ML Workloads](https://github.com/pacoxu/pacoxu/issues/76)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2025-11-26T10:25:12+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2025/11/26/kubernetes-introduces-native-gang-scheduling-support-to-better-serve-ai-ml-workloads/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2025-11-26`.
> Original URL: https://pacoxu.wordpress.com/2025/11/26/kubernetes-introduces-native-gang-scheduling-support-to-better-serve-ai-ml-workloads/
<h6>中文 <a href="https://mp.weixin.qq.com/s/EO0yfdVQMNgKI7nqkJ18Yw">https://mp.weixin.qq.com/s/EO0yfdVQMNgKI7nqkJ18Yw</a> Kubernetes 支持原生 Gang Scheduling ： 适应 AI/ML 工作负载<br /><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#gang-scheduling-comes-to-kubernetes-a-game-changer-for-aiml-workloads"></a></h6>

<h2>Introduction<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#introduction"></a></h2>

<p>Scheduling large workloads in Kubernetes has always been challenging. When you need to run distributed training jobs, batch processing tasks, or other multi-pod applications, the traditional pod-by-pod scheduling approach can lead to resource wastage, deadlocks, and inefficiencies. Today, we&#8217;re excited to share insights about the&nbsp;<strong>Workload Aware Scheduling</strong>&nbsp;initiative that&#8217;s transforming how Kubernetes handles multi-pod workloads.</p>

<h2>The Problem with Traditional Pod Scheduling<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#the-problem-with-traditional-pod-scheduling"></a></h2>

<p>In traditional Kubernetes scheduling, each pod is scheduled independently. For distributed workloads like:</p>

<ul>
<li><strong>Distributed ML training</strong> (e.g., PyTorch, TensorFlow multi-worker jobs)</li>

<li><strong>Batch processing</strong> (e.g., Apache Spark, Ray clusters)</li>

<li><strong>High-performance computing</strong> (e.g., MPI applications)</li>
</ul>

<p>This independent scheduling creates several problems:</p>

<ol>
<li><strong>Partial scheduling deadlocks</strong>: Some pods get scheduled while others wait indefinitely for resources</li>

<li><strong>Resource wastage</strong>: Scheduled pods consume resources but can&#8217;t start work until all peers are ready</li>

<li><strong>Poor cluster utilization</strong>: Resources are tied up by incomplete workloads</li>

<li><strong>Unpredictable job completion times</strong>: Jobs may wait hours or days in partially-scheduled states</li>
</ol>

<h2>Kubernetes v1.35: Workload Aware Scheduling<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#kubernetes-v135-workload-aware-scheduling"></a></h2>

<p>The Kubernetes community has introduced&nbsp;<strong>Workload Aware Scheduling</strong>&nbsp;in v1.35, featuring three major components:</p>

<h3>1. Workload API (Alpha)<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#1-workload-api-alpha"></a></h3>

<p>The new&nbsp;<code>Workload</code>&nbsp;API resource in&nbsp;<code>scheduling.k8s.io/v1alpha1</code>&nbsp;provides a structured way to define scheduling requirements for multi-pod applications.</p>

<pre>apiVersion: scheduling.k8s.io/v1alpha1
kind: Workload
metadata:
  name: training-job-workload
  namespace: ml-workloads
spec:
  podGroups:
  - name: workers
    policy:
      gang:
        # All-or-nothing: schedule only if 4 pods can run together
        minCount: 4</pre>

<p>Link your pods to the workload:</p>

<pre>apiVersion: v1
kind: Pod
metadata:
  name: worker-0
  namespace: ml-workloads
spec:
  workloadRef:
    name: training-job-workload
    podGroup: workers
  containers:
  - name: trainer
    image: my-ml-framework:latest
    resources:
      requests:
        nvidia.com/gpu: 1</pre>

<h3>2. Gang Scheduling (Alpha)<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#2-gang-scheduling-alpha"></a></h3>

<p>Gang scheduling implements the&nbsp;<strong>all-or-nothing</strong>&nbsp;placement strategy:</p>

<p><strong>How it works:</strong></p>

<ol>
<li><strong>Waiting Phase</strong>: When pods arrive, the scheduler blocks them until <code>minCount</code> pods are pending</li>

<li><strong>Evaluation Phase</strong>: The scheduler attempts to find suitable nodes for all pods in the gang</li>

<li><strong>Decision Phase</strong>:
<ul>
<li>✅ <strong>Success</strong>: If all pods can be placed, they&#8217;re bound to nodes together</li>

<li>❌ <strong>Failure</strong>: If any pod can&#8217;t be placed within timeout (5 minutes), ALL pods are rejected and requeued</li>
</ul>
</li>
</ol>

<p>This prevents resource waste and ensures your distributed workload either runs completely or waits for sufficient resources.</p>

<p><strong>Key benefits:</strong></p>

<ul>
<li>Eliminates partial scheduling deadlocks</li>

<li>Improves cluster utilization by freeing resources for runnable workloads</li>

<li>Provides predictable behavior for distributed applications</li>

<li>Works seamlessly with pod preemption and autoscaling</li>
</ul>

<h3>3. Opportunistic Batching (Beta)<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#3-opportunistic-batching-beta"></a></h3>

<p>Opportunistic Batching is a performance optimization that speeds up scheduling of identical pods without requiring any configuration changes.</p>

<p><strong>How it works:</strong></p>

<p>When the scheduler processes pods with identical scheduling requirements (same resources, images, affinities, etc.), it can reuse feasibility calculations and scoring results for subsequent pods in the queue.</p>

<p><strong>Performance impact:</strong></p>

<ul>
<li>Dramatically reduces scheduling latency for large homogeneous workloads</li>

<li>Can improve scheduling throughput by 5-10x for batch workloads</li>

<li>Works transparently &#8211; no user configuration needed</li>

<li>Enabled by default in Kubernetes v1.35 (Beta)</li>
</ul>

<p><strong>Current restrictions:</strong></p>

<ul>
<li>Disabled for pods using topology spread constraints</li>

<li>Disabled for pods using Dynamic Resource Allocation (DRA)</li>

<li>All scheduling-relevant pod fields must be identical</li>
</ul>

<h2>Real-World Use Cases<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#real-world-use-cases"></a></h2>

<h3>Distributed ML Training<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#distributed-ml-training"></a></h3>

<pre>apiVersion: scheduling.k8s.io/v1alpha1
kind: Workload
metadata:
  name: pytorch-training
spec:
  podGroups:
  - name: workers
    policy:
      gang:
        minCount: 8  # Need 8 GPUs for distributed training</pre>

<p>Your PyTorch distributed training job only starts when all 8 workers can be scheduled, preventing wasted GPU resources.</p>

<h3>Apache Spark on Kubernetes<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#apache-spark-on-kubernetes"></a></h3>

<pre>apiVersion: scheduling.k8s.io/v1alpha1
kind: Workload
metadata:
  name: spark-job
spec:
  podGroups:
  - name: executors
    policy:
      gang:
        minCount: 10  # 1 driver + 9 executors minimum</pre>

<p>Spark jobs with gang scheduling avoid the common problem where the driver starts but executors can&#8217;t be scheduled.</p>

<h3>Ray Clusters<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#ray-clusters"></a></h3>

<p>Ray applications benefit from gang scheduling by ensuring the head node and worker nodes start together, enabling immediate distributed computation.</p>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2025/11/image.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2025/11/image.png?w=720" alt="" /></a>

<h2>The Roadmap: What&#8217;s Coming in 1.36 and Beyond<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#the-roadmap-whats-coming-in-136-and-beyond"></a></h2>

<p>The Workload Aware Scheduling effort has an ambitious roadmap for Kubernetes 1.36:</p>

<h3>Planned for v1.36<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#planned-for-v136"></a></h3>

<ul>
<li><strong>Expanding Workload API</strong>: Enhanced capabilities and refinements based on alpha feedback</li>

<li><strong>Auto-workload for Job, StatefulSet, JobSet</strong>: Automatic workload creation for common Kubernetes resources</li>

<li><strong>Topology Aware Scheduling</strong>: Consider network and hardware topology when placing gang members</li>

<li><strong>Single-cycle workload scheduling</strong>: Schedule entire gangs in a single scheduling cycle for better performance</li>

<li><strong>Tree-based workload scheduling algorithm</strong>: More efficient gang placement decisions</li>

<li><strong>Improved binding process</strong>: Better handling of kubelet races using nominations</li>

<li><strong>Delayed preemption</strong>: Introduce nominating victims before actual eviction</li>

<li><strong>Workload-level preemption</strong>: Preempt entire gangs rather than individual pods</li>
</ul>

<h3>Long-term Vision<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#long-term-vision"></a></h3>

<p>The ultimate goal is to make Kubernetes natively understand and optimize for workload-level operations, including:</p>

<ul>
<li>Deep integration with cluster autoscaling</li>

<li>Workload-aware resource quotas and limits</li>

<li>Better support for mixed workload types (batch + serving)</li>

<li>Enhanced observability for multi-pod applications</li>
</ul>

<h2>Upcoming Official Blog Post<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#upcoming-official-blog-post"></a></h2>

<p>The Kubernetes community is preparing an official blog post about Workload Aware Scheduling that will be published soon on the Kubernetes blog. Watch for&nbsp;<a href="https://github.com/kubernetes/website/pull/53012">kubernetes/website#53012</a>&nbsp;to be merged for the official announcement.</p>

<h2>Getting Started<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#getting-started"></a></h2>

<h3>Prerequisites</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#prerequisites"></a></p>

<ul>
<li>Kubernetes v1.35 or later</li>

<li>Feature gates configured on kube-apiserver and kube-scheduler</li>
</ul>

<h3>Enable Workload API and Gang Scheduling<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#enable-workload-api-and-gang-scheduling"></a></h3>

<pre># On kube-apiserver
--feature-gates=GenericWorkload=true
--runtime-config=scheduling.k8s.io/v1alpha1=true

# On kube-scheduler
--feature-gates=GenericWorkload=true,GangScheduling=true</pre>

<h3>Enable Opportunistic Batching<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#enable-opportunistic-batching"></a></h3>

<p>Opportunistic Batching is&nbsp;<strong>enabled by default</strong>&nbsp;in v1.35 as a Beta feature. To disable it:</p>

<pre># On kube-scheduler
--feature-gates=OpportunisticBatching=false</pre>

<h3>Testing Gang Scheduling<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#testing-gang-scheduling"></a></h3>

<ol>
<li>Create a Workload resource</li>

<li>Create pods with <code>workloadRef</code> pointing to the Workload</li>

<li>Observe scheduling behavior in kube-scheduler logs</li>

<li>Monitor metrics for gang scheduling success/failure rates</li>
</ol>

<h2>Best Practices<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#best-practices"></a></h2>

<ol>
<li><strong>Set appropriate minCount</strong>: Consider your application&#8217;s minimum viable size</li>

<li><strong>Use resource requests accurately</strong>: Gang scheduling depends on accurate resource requirements</li>

<li><strong>Monitor scheduling metrics</strong>: Track gang scheduling success rates and timeout events</li>

<li><strong>Test with cluster autoscaling</strong>: Ensure your autoscaler can provision nodes for gangs</li>

<li><strong>Plan for failure scenarios</strong>: Understand timeout behavior and retry logic</li>
</ol>

<h2>Comparison with Existing Solutions<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#comparison-with-existing-solutions"></a></h2>

<p>Before native gang scheduling, users relied on:</p>

<ul>
<li><strong>Volcano</strong>: CNCF incubating project with gang scheduling</li>

<li><strong>Kueue</strong>: Kubernetes SIG project for queue and quota management</li>

<li><strong>YuniKorn</strong>: Apache project with gang scheduling support</li>

<li><strong>Custom schedulers</strong>: In-house solutions for specific use cases</li>
</ul>

<p><strong>Why use native gang scheduling?</strong></p>

<ul>
<li>Maintained by Kubernetes SIG Scheduling</li>

<li>Integrated with core scheduler features (preemption, autoscaling)</li>

<li>No additional components to deploy and maintain</li>

<li>Part of the Kubernetes conformance suite (eventually)</li>
</ul>

<p><strong>When to use external schedulers?</strong></p>

<ul>
<li>Need production-ready gang scheduling today (use Volcano or Kueue)</li>

<li>Require features beyond current Kubernetes roadmap</li>

<li>Have existing investments in specific schedulers</li>
</ul>

<h2>Resources and References<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#resources-and-references"></a></h2>

<h3>KEPs and Documentation<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#keps-and-documentation"></a></h3>

<ul>
<li><a href="https://github.com/kubernetes/enhancements/issues/4671">KEP-4671: Gang Scheduling</a></li>

<li><a href="https://github.com/kubernetes/enhancements/blob/master/keps/sig-scheduling/5598-opportunistic-batching/README.md">KEP-5598: Opportunistic Batching</a></li>

<li><a href="https://github.com/kubernetes/kubernetes/issues/132192">Workload Aware Scheduling Tracking Issue</a></li>

<li><a href="https://github.com/kubernetes/website/pull/53012">Kubernetes Website PR #53012</a></li>
</ul>

<h3>Related Projects</h3>

<p>Several projects currently support gang scheduling:<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#related-projects"></a></p>

<ul>
<li><a href="https://github.com/volcano-sh/volcano">Volcano Scheduler</a> &#8211; CNCF Incubating
<ul>
<li>Full gang scheduling support</li>

<li>Recently added LeaderWorkerSet (LWS) gang scheduling in v1.13 release</li>
</ul>
</li>

<li><a href="https://github.com/koordinator-sh/koordinator/">Koordinator</a> &#8211; Alibaba Open Source
<ul>
<li>Basic gang scheduling capabilities</li>

<li>Workload orchestration and resource scheduling enhancements</li>
</ul>
</li>

<li><a href="https://github.com/kubernetes-sigs/kueue">Kueue</a> &#8211; Kubernetes SIG Project
<ul>
<li>CoScheduling support (a lighter version of gang scheduling)</li>

<li>Focus on job queueing and quota management</li>
</ul>
</li>

<li><a href="https://yunikorn.apache.org/">YuniKorn</a> &#8211; Apache Project
<ul>
<li>Gang scheduling and resource scheduling capabilities</li>
</ul>
</li>
</ul>

<h3>Community<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#community"></a></h3>

<ul>
<li>SIG Scheduling: <a href="https://github.com/kubernetes/community/tree/master/sig-scheduling">https://github.com/kubernetes/community/tree/master/sig-scheduling</a></li>

<li>Slack: #sig-scheduling on Kubernetes Slack</li>
</ul>

<h2>Conclusion<a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-25/gang-scheduling.md#conclusion"></a></h2>

<p>Gang Scheduling and Workload Aware Scheduling represent a major step forward for Kubernetes in supporting AI/ML, HPC, and batch processing workloads. The v1.35 alpha release provides a foundation for native multi-pod scheduling, with an exciting roadmap for v1.36 and beyond.</p>

<p>We encourage the community to:</p>

<ul>
<li>Test these features in development environments</li>

<li>Provide feedback through GitHub issues</li>

<li>Share use cases and requirements</li>

<li>Contribute to the ongoing development</li>
</ul>

<p>The future of Kubernetes scheduling is workload-aware, and the journey has just begun!</p>
