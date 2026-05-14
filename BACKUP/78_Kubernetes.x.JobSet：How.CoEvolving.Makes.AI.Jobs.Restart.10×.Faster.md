# [Kubernetes x JobSet：How CoEvolving Makes AI Jobs Restart 10× Faster](https://github.com/pacoxu/pacoxu/issues/78)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2025-12-01T09:11:14+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2025/12/01/kubernetes-x-jobset%ef%bc%9ahow-coevolving-makes-ai-jobs-restart-10x-faster/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2025-12-01`.
> Original URL: https://pacoxu.wordpress.com/2025/12/01/kubernetes-x-jobset%ef%bc%9ahow-coevolving-makes-ai-jobs-restart-10x-faster/
<p><a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/blog/2025-11-26/jobset-in-place-restart.md#jobset-in-place-restart-from-2m10s-to-10s--a-92-speed-boost"></a></p>

<h2>Co-Evolving: When Kubernetes Features Empower the Ecosystem</h2>

<p>In the rapidly evolving AI infrastructure landscape, a beautiful synergy is<br />emerging: the Kubernetes community develops foundational capabilities, and<br />downstream projects like <a href="https://github.com/kubernetes-sigs/jobset">JobSet</a>,<br /><a href="https://github.com/ray-project/ray">Ray</a>, and<br /><a href="https://github.com/kubernetes-sigs/lws">LeaderWorkerSet (LWS)</a> adopt these<br />features to dramatically improve their efficiency. We call this <strong>Co-Evolving</strong><br />(协同演进) — the entire ecosystem advancing together.</p>

<p>Kubernetes has been introducing more AI-related capabilities recently, but<br />realizing their full potential in AI workloads requires adaptation by other<br />projects. Today, we&#8217;ll explore a prime example: <strong>JobSet leveraging Kubernetes In-Place Container Restart to achieve 92% faster restart times</strong>.</p>

<h2>The Problem: Slow JobSet Restart</h2>

<p>When a distributed training job running on<br /><a href="https://github.com/kubernetes-sigs/jobset">JobSet</a> needs to restart (due to<br />transient failures, configuration updates, or checkpoint recovery), the<br />traditional approach involves:</p>

<ol>
<li><strong>Delete all pods</strong> in the JobSet</li>

<li><strong>Wait for pod termination</strong> to complete</li>

<li><strong>Reschedule all pods</strong> through the Kubernetes scheduler</li>

<li><strong>Wait for pod startup</strong> (including image pulls, init containers, etc.)</li>
</ol>

<p>In a large-scale cluster with 5000 nodes, this process takes approximately<br /><strong>2 minutes and 10 seconds</strong>. For AI/ML workloads where fast recovery is<br />critical, this overhead is significant.</p>

<h2>The Solution: In-Place Container Restart</h2>

<p>Kubernetes has introduced capabilities that allow containers to restart without<br />pod recreation:</p>

<h3>KEP-5307: Container Restart Policy (Kubernetes 1.34)</h3>

<p><a href="https://github.com/kubernetes/enhancements/blob/master/keps/sig-node/5307-container-restart-policy/README.md">KEP-5307</a><br />introduces fine-grained control over individual container restart behavior<br />within pods. This allows:</p>

<ul>
<li>Specifying restart policies per container (not just per pod)</li>

<li>Triggering container restarts without affecting the entire pod</li>

<li>Maintaining pod identity, IP, and volumes during container restarts</li>
</ul>

<h3>KEP-5532: Restart All Containers on Container Exits (Kubernetes 1.35)</h3>

<p><a href="https://github.com/kubernetes/enhancements/blob/master/keps/sig-node/5532-restart-all-containers-on-container-exits/README.md">KEP-5532</a><br />extends this capability to enable coordinated restarts:</p>

<ul>
<li>Restart all containers in a pod when specific containers exit</li>

<li>Restart init containers and sidecars as part of the pod lifecycle</li>

<li>Enable pod-level restart coordination without pod recreation</li>
</ul>

<h2>Real-World Results: JobSet In-Place Restart</h2>

<p>The JobSet team has developed an<br /><a href="https://github.com/kubernetes-sigs/jobset/compare/main…GiuseppeTT:jobset:in-place-restart-prototype">in-place restart prototype</a><br />that demonstrates remarkable performance improvements:</p>

<table><thead><tr><th>Metric</th><th>Traditional Restart</th><th>In-Place Restart</th><th>Improvement</th></tr></thead><tbody><tr><td>Restart Time</td><td>2m10s</td><td>10s</td><td><strong>92% faster</strong></td></tr><tr><td>Test Scale</td><td>5000 nodes</td><td>5000 nodes</td><td>&#8211;</td></tr><tr><td>Scheduling Overhead</td><td>High</td><td>None</td><td>Eliminated</td></tr><tr><td>Pod Recreation</td><td>Required</td><td>Not needed</td><td>Avoided</td></tr></tbody></table>

<p>For detailed design information, see the<br /><a href="https://docs.google.com/document/d/16zexVooHKPc80F4dVtUjDYK9DOpkVPRNfSv0zRtfFpk/edit?tab=t.0#heading=h.y6xl7juq7465">JobSet in-place restart design document</a>.</p>

<h2>Why This Matters for AI Workloads</h2>

<h3>1. Distributed Training Recovery</h3>

<p>Large-scale distributed training jobs (PyTorch DDP, TensorFlow MultiWorkerMirroredStrategy)<br />are particularly sensitive to restart latency:</p>

<ul>
<li><strong>Checkpoint recovery</strong>: After a failure, all workers need to restart from<br />the latest checkpoint. In-place restart gets workers back online 12x faster.</li>

<li><strong>Gradient synchronization</strong>: All workers must be running for training to<br />proceed. Faster restarts mean less wasted GPU time.</li>

<li><strong>Cost savings</strong>: On expensive GPU clusters ($2-10/GPU-hour), 2 minutes saved<br />per restart adds up significantly.</li>
</ul>

<h3>2. Job Dependencies</h3>

<p>Many AI pipelines have complex job dependencies. When a job restarts:</p>

<ul>
<li><strong>Downstream jobs</strong> wait for upstream completion</li>

<li><strong>Gang scheduling constraints</strong> require all workers to be present</li>

<li><strong>Network connectivity</strong> must be maintained for collective operations</li>
</ul>

<p>In-place restart preserves pod identity and network connectivity, minimizing<br />disruption to the overall pipeline.</p>

<h3>3. Resource Efficiency</h3>

<p>Traditional restart involves:</p>

<ul>
<li><strong>Scheduler load</strong>: Finding nodes for potentially thousands of pods</li>

<li><strong>API server load</strong>: Creating/deleting pod objects</li>

<li><strong>Node preparation</strong>: Image pulls, volume mounts, init containers</li>
</ul>

<p>In-place restart eliminates all of this overhead, keeping resources available<br />for actual workloads.</p>

<h2>How It Works</h2>

<h3>Before: Traditional Restart Flow</h3>

<pre>
Job Restart Triggered
    ↓
Delete All Pods → Wait for Termination (30s+)
    ↓
Create New Pods → Wait for Scheduling (30s+)
    ↓
Pull Images (if needed) → Start Containers (60s+)
    ↓
Total: ~2m10s
</pre>

<h3>After: In-Place Restart Flow</h3>

<pre>
Job Restart Triggered
    ↓
Signal Container Exit → Container Restarts In-Place (10s)
    ↓
Total: ~10s
</pre>

<p>The key differences:</p>

<ol>
<li><strong>No pod deletion</strong>: Pod objects remain, preserving identity</li>

<li><strong>No rescheduling</strong>: Pods stay on their current nodes</li>

<li><strong>No image pulls</strong>: Images are already cached on nodes</li>

<li><strong>Immediate restart</strong>: Container process simply restarts</li>
</ol>

<h2>Implementation Considerations</h2>

<h3>When to Use In-Place Restart</h3>

<ul>
<li><strong>Transient failures</strong>: Container crashes, OOM kills, network timeouts</li>

<li><strong>Configuration updates</strong>: Restart to pick up new environment variables</li>

<li><strong>Checkpoint recovery</strong>: Resume training from saved state</li>

<li><strong>Rolling updates</strong>: Graceful restart of workers in sequence</li>
</ul>

<h3>When Traditional Restart is Needed</h3>

<ul>
<li><strong>Node failures</strong>: Pod must move to a healthy node</li>

<li><strong>Resource changes</strong>: Pod needs more/less resources (consider VPA)</li>

<li><strong>Image updates</strong>: New container image required</li>

<li><strong>Topology changes</strong>: Pod needs different placement</li>
</ul>

<h3>Integration with JobSet</h3>

<p>JobSet can leverage in-place restart through:</p>

<pre>
apiVersion: jobset.x-k8s.io/v1alpha2
kind: JobSet
metadata:
  name: distributed-training
spec:
  replicatedJobs:
  - name: workers
    replicas: 8
    template:
      spec:
        template:
          spec:
            restartPolicy: Always  # Enables in-place restart
            containers:
            - name: trainer
              image: pytorch/pytorch:latest
</pre>

<h2>The Broader Co-Evolving Pattern</h2>

<p>This JobSet improvement exemplifies the Co-Evolving pattern in cloud-native AI:</p>

<table><thead><tr><th>Kubernetes Capability</th><th>Project Adoption</th><th>Benefit</th></tr></thead><tbody><tr><td>In-Place Restart</td><td>JobSet</td><td>92% faster recovery</td></tr><tr><td>Gang Scheduling (1.35)</td><td>Kueue, LWS</td><td>All-or-nothing placement</td></tr><tr><td>DRA (1.34 GA)</td><td>NVIDIA GPU Operator</td><td>Flexible device allocation</td></tr><tr><td>Workload API (1.35)</td><td>Volcano, YuniKorn</td><td>Native workload support</td></tr></tbody></table>

<p>As Kubernetes continues to add AI-friendly features, we expect more projects<br />to adopt them, creating a virtuous cycle of improvement.</p>

<h2>Getting Started</h2>

<h3>Prerequisites</h3>

<ul>
<li>Kubernetes 1.34+ (for KEP-5307)</li>

<li>Kubernetes 1.35+ (for KEP-5532 pod-level restart)</li>

<li>JobSet with in-place restart support (check latest releases)</li>
</ul>

<h3>Enable Feature Gates</h3>

<pre>
# On kubelet for KEP-5307 (Container Restart Policy, 1.34+)
--feature-gates=ContainerRestartPolicy=true

# On kubelet for KEP-5532 (Restart All Containers, 1.35+)
--feature-gates=RestartAllContainersOnContainerExits=true
</pre>

<h3>Test In-Place Restart</h3>

<ol>
<li>Deploy a JobSet with <code>restartPolicy: Always</code></li>

<li>Trigger a container restart (e.g., <code>kubectl exec ... -- kill -TERM 1</code>)</li>

<li>Observe the restart time compared to pod recreation</li>
</ol>

<h2>Future Roadmap</h2>

<p>The in-place restart capability continues to evolve:</p>

<ul>
<li><strong>KEP-5307 graduation</strong>: Moving toward Beta/GA</li>

<li><strong>KEP-5532 graduation</strong>: Enhanced pod-level restart control</li>

<li><strong>JobSet integration</strong>: Native support for in-place restart policies</li>

<li><strong>Monitoring</strong>: Better observability for restart events</li>

<li><strong>Kueue integration</strong>: Workload-aware restart handling</li>
</ul>

<h2>Conclusion</h2>

<p>The JobSet in-place restart optimization demonstrates the power of Co-Evolving<br />in the Kubernetes ecosystem. By adopting upstream Kubernetes capabilities,<br />projects can achieve dramatic performance improvements:</p>

<ul>
<li><strong>92% faster restart</strong> (2m10s → 10s)</li>

<li><strong>No scheduling overhead</strong></li>

<li><strong>Preserved pod identity and network</strong></li>

<li><strong>Reduced API server load</strong></li>
</ul>

<p>This is just one example of how the Kubernetes community and downstream<br />projects work together to improve AI workload efficiency. As more AI-related<br />features land in Kubernetes, we can expect even more optimizations from<br />projects like JobSet, Ray, LWS, and others.</p>

<p>The future of AI infrastructure is Co-Evolving — and it&#8217;s happening now.</p>

<hr />

<h2>References</h2>

<h3>KEPs and Documentation</h3>

<ul>
<li><a href="https://github.com/kubernetes/enhancements/blob/master/keps/sig-node/5307-container-restart-policy/README.md">KEP-5307: Container Restart Policy</a></li>

<li><a href="https://github.com/kubernetes/enhancements/blob/master/keps/sig-node/5532-restart-all-containers-on-container-exits/README.md">KEP-5532: Restart All Containers on Container Exits</a></li>

<li><a href="https://github.com/kubernetes/enhancements/blob/master/keps/sig-node/1287-in-place-update-pod-resources/README.md">KEP-1287: In-Place Pod Vertical Scaling</a></li>

<li><a href="https://docs.google.com/document/d/16zexVooHKPc80F4dVtUjDYK9DOpkVPRNfSv0zRtfFpk/edit?tab=t.0#heading=h.y6xl7juq7465">JobSet In-Place Restart Design Document</a></li>

<li><a href="https://github.com/kubernetes-sigs/jobset/compare/main…GiuseppeTT:jobset:in-place-restart-prototype">JobSet In-Place Restart Prototype</a></li>
</ul>

<h3>Related Projects</h3>

<ul>
<li><a href="https://github.com/kubernetes-sigs/jobset">JobSet</a> &#8211; Kubernetes SIG Apps</li>

<li><a href="https://github.com/kubernetes-sigs/lws">LeaderWorkerSet</a> &#8211; Kubernetes SIG Apps</li>

<li><a href="https://github.com/kubernetes-sigs/kueue">Kueue</a> &#8211; Kubernetes SIG Scheduling</li>

<li><a href="https://github.com/volcano-sh/volcano">Volcano</a> &#8211; CNCF Incubating</li>
</ul>

<h3>Related Blog Posts</h3>

<ul>
<li><a href="../2025-11-25/gang-scheduling.md">Gang Scheduling in Kubernetes</a></li>

<li><a href="../../kubernetes/scheduling-optimization.md">Scheduling Optimization</a></li>
</ul>
