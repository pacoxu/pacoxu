# [Kubernetes Pod Startup Speed Optimization Guide](https://github.com/pacoxu/pacoxu/issues/83)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2026-01-30T10:15:48+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2026/01/30/kubernetes-pod-startup-speed-optimization-guide/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2026-01-30`.
> Original URL: https://pacoxu.wordpress.com/2026/01/30/kubernetes-pod-startup-speed-optimization-guide/
<p>Pod startup speed is often overlooked in cloud-native environments, yet its impact extends across multiple dimensions of system performance and cost. Consider a scenario where traffic suddenly surges and the auto-scaling system needs to quickly spin up new Pods to handle the load. If each Pod takes tens of seconds or even minutes to become fully operational, those incoming requests during the startup window will likely be dropped, degrading user experience. This isn&#8217;t merely a performance issue—it&#8217;s a cost issue, as idle compute resources consume expenses every single second.</p>

<h2>Why Pod Startup Speed Matters<a href="https://github.com/pacoxu/AI-Infra/blob/2c723e344371e8453a12573209a8d87159891608/docs/blog/2026-01-28/pod-startup-speed.md#why-pod-startup-speed-matters"></a></h2>

<p>Pod startup performance touches several critical concerns. First is the need for rapid scaling. When applications require autoscaling, startup speed determines how quickly the system can respond to traffic fluctuations. Second is resource efficiency. Faster startup means less wasted idle resources. Third is user experience, especially in serverless architectures where cold start latency directly impacts the application response time users perceive. Finally, from a cost perspective, reducing Pod startup time significantly lowers infrastructure expenses.</p>

<h2>The Four Key Points of Pod Startup</h2>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2026/01/image.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2026/01/image.png?w=1024" alt="" /></a>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/2c723e344371e8453a12573209a8d87159891608/docs/blog/2026-01-28/pod-startup-speed.md#the-four-key-stages-of-pod-startup"></a></p>

<p>Understanding the various stages of Pod startup is essential to optimization efforts. The Pod startup process can be divided into four major phases: API Server processing, scheduling, pod startup on node, and application start-to-ready.</p>

<p>The API Server processing phase involves Pod object creation, validation, and persistence. During this phase, the control plane must handle the request, execute admission control policies, and write the Pod object to etcd. While typically fast, this process can become a bottleneck in high-concurrency scenarios.</p>

<p>The scheduling phase spans from Pod creation to being scheduled on a specific node. The scheduler must evaluate all available nodes and select the most suitable target. The duration depends on cluster size and scheduler configuration. In large-scale clusters, this can become a significant source of latency.</p>

<p>The node startup phase encompasses pulling images, creating containers, and starting processes on the selected node. This is usually the longest phase in the entire Pod startup process. It includes network image pulls, storage volume initialization, application startup, and health check completion.</p>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2026/01/image-1.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2026/01/image-1.png?w=701" alt="" /></a>

<p>The ready phase, while not strictly part of the &#8220;startup&#8221; process, affects how the system perceives Pod readiness. If health checks are misconfigured, a Pod might be running but considered unready, affecting overall startup time metrics.</p>

<h2>Optimizing the API Server Processing Stage<a href="https://github.com/pacoxu/AI-Infra/blob/2c723e344371e8453a12573209a8d87159891608/docs/blog/2026-01-28/pod-startup-speed.md#optimizing-the-api-server-processing-stage"></a></h2>

<p>At the API Server level, the focus is on improving throughput and reducing latency. A straightforward but effective optimization is adjusting the API Server&#8217;s concurrent request handling capacity. Increasing the&nbsp;<code>--max-requests-inflight</code>&nbsp;and&nbsp;<code>--max-mutating-requests-inflight</code>&nbsp;parameters allows the API Server to handle more Pod creation requests simultaneously.</p>

<p>Another crucial optimization is streamlining admission controllers. Some controllers might perform expensive operations, such as accessing external services or executing complex validations. Consider disabling unnecessary admission controllers or configuring them for maximum efficiency. Similarly, ensuring excellent etcd performance is vital, as the API Server ultimately must persist Pod objects to etcd.</p>

<h2>Optimizing the Scheduling Phase</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/2c723e344371e8453a12573209a8d87159891608/docs/blog/2026-01-28/pod-startup-speed.md#optimizing-the-scheduling-phase"></a></p>

<p>The scheduler&#8217;s performance directly impacts the time from Pod creation to scheduling. Leveraging various optimization techniques provided by the scheduling framework can accelerate this process. For instance, the pre-filter and filter phases can quickly eliminate unsuitable nodes, reducing the number of candidates for subsequent scoring phases.</p>

<p>Another key optimization involves judiciously using node affinity and Pod affinity rules while avoiding overly complex rules that increase scheduling latency. Additionally, for specific workloads, using priority and preemption features can ensure critical Pods are scheduled faster.</p>

<p>In large-scale clusters, consider deploying multiple scheduler instances to distribute the load. Kubernetes natively supports running multiple scheduler instances concurrently, which can significantly boost scheduling throughput.</p>

<h2>Optimizing the Node Startup Phase</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/2c723e344371e8453a12573209a8d87159891608/docs/blog/2026-01-28/pod-startup-speed.md#optimizing-the-node-startup-phase"></a></p>

<p>This phase offers the most substantial optimization opportunities. First, image pulling is a major bottleneck. Image warming is a proven optimization strategy. Pre-pull commonly used images to nodes during startup or scheduled maintenance windows. When Pods actually launch, they won&#8217;t need to fetch images from remote registries, drastically reducing startup time.</p>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2026/01/image-2.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2026/01/image-2.png?w=687" alt="" /></a>

<p>There are many ways to improve image pull speed. These include best practices for reducing image size, configuring Kubelet to enable concurrent image pulls, and adopting P2P distribution (such as Dragonfly or Uber/Kraken) or lazy loading mechanisms (such as stargz-snapshotter and Nydus). How to accelerate Pod startup under large-scale concurrency has been discussed in the context of VKE’s practices using Dragonfly and Nydus.</p>

<p>Container runtime performance is also critical. Different runtimes (such as containerd and Docker) have different performance characteristics. containerd is generally considered more lightweight and efficient, especially at large scale. Regularly upgrading the runtime to the latest version can also bring performance improvements. Slow <code>docker create</code> / <code>docker run</code> behavior is very common: it is usually caused by too many containers or images on a node (which can be mitigated by scheduled cleanup jobs). The legacy devicemapper storage driver is significantly slower in scenarios with frequent container creation and deletion; overlayfs performs somewhat better. In addition, older Docker versions contain many minor bugs that can cause <code>docker ps</code> or <code>docker run</code> to hang.</p>

<p>Application startup time itself also deserves attention. Some applications perform a large amount of initialization work at startup, such as database migrations or cache warm-up. Making these tasks asynchronous or deferring them until after the application has started can significantly reduce perceived startup latency.</p>

<p>CPU throttling during startup is another common issue. For a detailed discussion of CPU throttling in Kubernetes, possible mitigations include increasing CPU limits, pinning CPUs, or bypassing the issue via VPA-based approaches. (For cold-start scenarios with VPA, see: <em>After waiting six years, Kubernetes 1.35 finally reaches GA with in-place resizing, boosting Java startup speed by 70%!</em>)</p>

<p>Init containers can be used to perform necessary setup before the main container starts. However, init containers run sequentially, so it is important to avoid excessive initialization steps. Only perform what is strictly necessary and parallelize where possible. If feasible, use PostStart hooks to avoid delaying the main container startup. Complete preparation as early as possible: can these tasks be done during image build time? Can they be handled by a DaemonSet or Pod on the node? All of these approaches help reduce the preparation time before the Pod’s main container starts.</p>

<h2>Optimizing Observability and Health Checks<a href="https://github.com/pacoxu/AI-Infra/blob/2c723e344371e8453a12573209a8d87159891608/docs/blog/2026-01-28/pod-startup-speed.md#optimizing-observability-and-health-checks"></a></h2>

<p>Health check configuration has a significant impact on startup time metrics. If a StartupProbe is configured, the <code>initialDelaySeconds</code> of the ReadinessProbe should be reduced.</p>

<p>If no StartupProbe is configured, an appropriate <code>initialDelaySeconds</code> must be set for the ReadinessProbe.</p>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2026/01/image-3.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2026/01/image-3.png?w=691" alt="" /></a>

<p>At the same time, health checks must remain sufficiently strict to ensure that unhealthy Pods are not mistakenly considered ready.</p>

<p>Startup probes allow applications enough time to complete initialization without being killed or restarted during the startup phase.</p>

<h2>Checkpointing and Snapshots<a href="https://github.com/pacoxu/AI-Infra/blob/2c723e344371e8453a12573209a8d87159891608/docs/blog/2026-01-28/pod-startup-speed.md#cutting-edge-technologies-checkpointing-and-snapshots"></a></h2>

<p>The Kubernetes community is exploring the use of checkpointing techniques to accelerate Pod startup. Checkpointing allows the state of a running container to be saved and later restored quickly, thereby skipping the application’s normal startup process. This is particularly beneficial for applications with long startup times.</p>

<p>For example, <strong>CRIU</strong> (Checkpoint/Restore In Userspace) has been integrated into the container runtimes used by <strong>Kubernetes</strong>. By saving a container’s state at a certain point in time—including memory and filesystem state—it can be rapidly restored when needed, effectively enabling a “warm start.” This approach is especially promising for serverless computing and batch workloads.</p>

<h2>Kubelet configuration</h2>

<p>Kubernetes 1.27: updates on speeding up Pod startup</p>

<p><a href="https://kubernetes.io/blog/2023/05/15/speed-up-pod-startup/">https://kubernetes.io/blog/2023/05/15/speed-up-pod-startup/</a></p>

<p>This post points out a common issue in versions prior to 1.27, where Pods could start slowly and node-side events such as volume mount failures would occur.</p>

<p>To speed up Pod startup on nodes hosting multiple Pods—especially during sudden scale-up or scale-down events—the kubelet needs to synchronize Pod state and prepare ConfigMaps, Secrets, or volumes. This requires high-bandwidth access to the kube-apiserver.</p>

<p>In versions prior to v1.27, the default value of <code>kubeAPIQPS</code> was 5 and <code>kubeAPIBurst</code> was 10. Starting from v1.27, to improve Pod startup performance, the kubelet increased these defaults to 50 and 100 respectively. It is worth noting that raising the kubelet API QPS limits is not the only factor contributing to the performance improvement.</p>

<h2>Comprehensive Optimization Strategy<a href="https://github.com/pacoxu/AI-Infra/blob/2c723e344371e8453a12573209a8d87159891608/docs/blog/2026-01-28/pod-startup-speed.md#comprehensive-optimization-strategy"></a></h2>

<p>Pod startup optimization isn&#8217;t an isolated effort but requires a systematic, layered approach. From the API Server to the scheduler, container runtime, and application layer, every level offers optimization opportunities.</p>

<p>Establishing clear Pod startup time metrics is an essential first step. Clearly defining what constitutes startup time (from Pod creation to container running, or to Pod readiness?) is important. Using Prometheus or other monitoring tools to collect detailed startup metrics helps identify where the real bottlenecks are.</p>

<p>Priorities differ based on specific business needs and cluster characteristics. For high-traffic services requiring rapid scaling, image warming and startup probe tuning might yield the best results. For applications with long startup times, checkpoint technology might provide more value. For large-scale clusters, scheduler performance optimization and multiple scheduler instances might be key.</p>

<p>Finally, remember that optimization is a continuous process. Regularly reviewing and testing new optimization strategies, along with performance improvements from new Kubernetes versions, ensures your cluster maintains optimal performance.</p>

<hr />

<h2>Related Resources</h2>

<p>【KubeCon China 2023】How Can Pod Start-up Be Accelerated on Nodes in Large Clusters? &#8211; Paco Xu, DaoCloud &amp; Byron Wang <a href="https://www.youtube.com/@cncf"></a><a href="https://www.youtube.com/watch?v=UfjSphSD1Uk&amp;pp=2AYD">https://www.youtube.com/watch?v=UfjSphSD1Uk&amp;pp=2AYD</a><a href="https://github.com/pacoxu/AI-Infra/blob/2c723e344371e8453a12573209a8d87159891608/docs/blog/2026-01-28/pod-startup-speed.md#related-resources"></a></p>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/kubernetes/pod-lifecycle.md">https://github.com/pacoxu/AI-Infra/blob/main/docs/kubernetes/pod-lifecycle.md</a><a href="https://github.com/pacoxu/AI-Infra/blob/2c723e344371e8453a12573209a8d87159891608/docs/blog/2026-01-28/pod-startup-speed.md#kubernetes-pod-startup-speed-optimization-guide"></a></p>
