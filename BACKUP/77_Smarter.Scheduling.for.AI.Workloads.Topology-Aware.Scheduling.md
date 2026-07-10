# [Smarter Scheduling for AI Workloads: Topology-Aware Scheduling](https://github.com/pacoxu/pacoxu/issues/77)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2025-11-28T11:37:28+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2025/11/28/smarter-scheduling-for-ai-workloads-topology-aware-scheduling/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2025-11-28`.
> Original URL: https://pacoxu.wordpress.com/2025/11/28/smarter-scheduling-for-ai-workloads-topology-aware-scheduling/
<h2>Why Topology? Why Now?</h2>

<p>At KubeCon NA 2025, one theme dominated conversations in the AI/ML space:<br /><strong>topology</strong>. Everyone is talking about topology-aware scheduling because it&#8217;s<br />critical for optimizing AI workload performance.</p>

<img src="https://github.com/user-attachments/assets/ac793010-3bd2-49a1-a0d3-4d1ec14b5154" alt="Why Topology? Why Now?" />

<p><em>Source: <a href="https://www.youtube.com/watch?v=o5i7pTWZjfo">Lightning Talk: Mind the Topology &#8211; Roman Baron, NVIDIA</a></em></p>

<p>Modern AI workloads, especially distributed training and high-performance<br />inference, are extremely sensitive to hardware topology. When GPUs, NICs, CPUs,<br />and memory are not properly aligned within the same NUMA node, PCIe root, or<br />network fabric, performance can degrade by 30-50% or more.</p>

<h2>Background: Current Topology Scheduling Support</h2>

<h3>Device Plugin: The Traditional Approach</h3>

<p>Kubernetes Device Plugins have been the standard mechanism for managing<br />hardware resources like GPUs. The Device Plugin API provides:</p>

<img src="https://github.com/user-attachments/assets/3e642849-5879-4112-912b-6149825decce" alt="Device Management with Device Plugin" />

<p><em>Source: <a href="https://www.youtube.com/watch?v=j6zkGxrxm6o&amp;t=1007s">KubeCon NA 2025: Device Management</a></em></p>

<p><strong>Key Components:</strong></p>

<ul>
<li><strong>GetDevicePluginOptions</strong>: Plugin configuration</li>

<li><strong>ListAndWatch</strong>: Report available devices to kubelet</li>

<li><strong>GetPreferredAllocation</strong>: Suggest optimal device allocation (topology hint)</li>

<li><strong>Allocate</strong>: Perform device allocation for containers</li>

<li><strong>PreStartContainer</strong>: Pre-container-start hooks</li>
</ul>

<p><strong>Device Plugin supports:</strong></p>

<ul>
<li>Basic GPU counting (e.g., <code>nvidia.com/gpu: 8</code>)</li>

<li>MIG (Multi-Instance GPU) partitioning</li>

<li>Time-slicing for GPU oversubscription</li>
</ul>

<h3>Limitations of Device Plugin</h3>

<p>However, Device Plugins have significant limitations for topology-aware<br />scheduling:</p>

<img src="https://github.com/user-attachments/assets/a35ef2f0-a48a-47d3-b541-6a38b731931a" alt="Limitations of Device Plugin Management" />

<p><em>Source: <a href="https://www.youtube.com/watch?v=j6zkGxrxm6o&amp;t=1007s">KubeCon NA 2025: Device Management</a></em></p>

<ol>
<li><strong>Static isolation config</strong>: MIG configurations must be pre-defined</li>

<li><strong>Static slicing config</strong>: Time-slicing ratios are fixed at deployment</li>

<li><strong>Only even sharing expected</strong>: Limited sharing granularity</li>

<li><strong>Requires secondary scheduler</strong>: Complex topologies need additional<br />schedulers like Volcano or Kueue</li>
</ol>

<h3>Kueue: Topology-Aware Scheduling</h3>

<p><a href="https://github.com/kubernetes-sigs/kueue">Kueue</a> provides topology-aware<br />scheduling through node labels. It uses hierarchical topology levels like:</p>

<pre>
# Node labels for rack/block topology
cloud.google.com/gce-topology-block: &quot;block-1&quot;
cloud.google.com/gce-topology-subblock: &quot;subblock-1&quot;
cloud.google.com/gce-topology-host: &quot;host-1&quot;
kubernetes.io/hostname: &quot;node-1&quot;
</pre>

<p>Kueue supports:</p>

<ul>
<li><strong>TopologyAwareScheduling</strong>: Place workload pods on nodes with matching<br />topology</li>

<li><strong>Cohort-based resource sharing</strong>: Share resources within topology groups</li>

<li><strong>Gang scheduling with topology</strong>: Ensure all gang members are<br />topology-aligned</li>
</ul>

<p>Kueue Topology Configuration Example:</p>

<pre>
apiVersion: kueue.x-k8s.io/v1beta1
kind: ResourceFlavor
metadata:
  name: gpu-topology
spec:
  nodeLabels:
    cloud.google.com/gce-topology-block: &quot;block-1&quot;
  nodeTaints:
  - effect: NoSchedule
    key: nvidia.com/gpu
    value: &quot;present&quot;
</pre>

<h3>Volcano: Gang Scheduling with Topology</h3>

<p><a href="https://github.com/volcano-sh/volcano">Volcano</a> provides advanced scheduling<br />features including:</p>

<ul>
<li><strong>Gang scheduling</strong>: All-or-nothing scheduling for distributed workloads</li>

<li><strong>Topology plugin</strong>: Consider GPU topology in scheduling decisions</li>

<li><strong>Network-aware scheduling</strong>: RDMA/InfiniBand fabric awareness</li>
</ul>

<pre>
apiVersion: scheduling.volcano.sh/v1beta1
kind: PodGroup
metadata:
  name: distributed-training
spec:
  minMember: 8
  minResources:
    nvidia.com/gpu: &quot;8&quot;
  queue: training-queue
  # Topology affinity for NVLink connectivity
  topologyPolicy: &quot;best-effort&quot;
</pre>

<hr />

<h2>DRA: The Next Generation of Topology Management</h2>

<p><a href="https://github.com/kubernetes/dynamic-resource-allocation/">Dynamic Resource Allocation (DRA)</a><br />represents a fundamental shift in how Kubernetes handles device topology. DRA<br />provides structured parameters that enable rich topology expression and<br />constraint specification.</p>

<h3>How DRA Handles Topology-Aware Scheduling</h3>

<p>DRA uses <strong>attributes</strong> and <strong>constraints</strong> with CEL (Common Expression<br />Language) to express topology requirements. The key mechanisms include:</p>

<ol>
<li><strong>Device Attributes</strong>: Each device publishes topology information</li>
</ol>

<ul>
<li><code>pcieRoot</code>: PCIe hierarchy identifier</li>

<li><code>numaNode</code>: NUMA node association</li>

<li><code>nvlinkDomain</code>: NVLink fabric identifier</li>

<li><code>rdmaDevice</code>: Associated RDMA NIC</li>
</ul>

<ol>
<li><strong>Constraints</strong>: CEL expressions that enforce topology rules</li>
</ol>

<ul>
<li>Same PCIe root for GPU and NIC</li>

<li>Same NUMA node for CPU and memory</li>

<li>NVLink connectivity between GPUs</li>
</ul>

<ol>
<li><strong>SharedID</strong>: Devices on the same topology domain get a shared identifier</li>
</ol>

<h3>GPU + NIC Topology Coordination</h3>

<p>The most powerful use case for DRA topology is coordinating GPU and NIC<br />allocation on the same PCIe root. This is critical for RDMA-based distributed<br />training where GPU-Direct is used.</p>

<p>ResourceClaimTemplate with PCIe Topology Constraint Example:</p>

<pre>
apiVersion: resource.k8s.io/v1beta1
kind: ResourceClaimTemplate
metadata:
  name: gpu-nic-topology
spec:
  spec:
    devices:
      requests:
      - name: gpu
        deviceClassName: nvidia-gpu
        count: 1
      - name: rdma-nic
        deviceClassName: rdma-nic
        count: 1
      constraints:
      # GPU and NIC must be on the same PCIe root
      - requests: &#91;&quot;gpu&quot;, &quot;rdma-nic&quot;]
        matchAttribute: pcieRoot
</pre>

<p><strong>How this works:</strong></p>

<ol>
<li>The DRA scheduler evaluates available GPUs and NICs</li>

<li>For each candidate GPU, it finds NICs on the same PCIe root</li>

<li>Only allocations satisfying the constraint are considered</li>

<li>The <code>matchAttribute: pcieRoot</code> ensures both devices share the same<br />PCIe topology</li>
</ol>

<h3>DRANET: Network Device DRA</h3>

<p><a href="https://github.com/google/dranet">DRANET</a> is Google&#8217;s DRA implementation for<br />network devices. It integrates with Kueue&#8217;s topology-aware scheduling using<br />node labels:</p>

<pre>
# DRANET uses these labels for topology awareness
cloud.google.com/gce-topology-block
cloud.google.com/gce-topology-subblock
cloud.google.com/gce-topology-host
kubernetes.io/hostname
</pre>

<p>DRANET + NVIDIA GPU DRA can coordinate:</p>

<ul>
<li>RDMA NICs allocated with GPUs on same PCIe fabric</li>

<li>Multi-NIC configurations for distributed training</li>

<li>Network isolation using SR-IOV VFs</li>
</ul>

<h3>CPU Micro-Topology Support</h3>

<p>The <a href="https://github.com/kubernetes-sigs/dra-driver-cpu/pull/16">dra-driver-cpu</a><br />project is adding CPU micro-topology support including:</p>

<ul>
<li>NUMA-aware CPU allocation</li>

<li>CPU pinning with topology alignment</li>

<li>Coordination with GPU NUMA placement</li>
</ul>

<hr />

<h2>DRAConsumableCapacity: New in Kubernetes 1.34</h2>

<p>A major advancement in DRA is the <strong>DRAConsumableCapacity</strong> feature:</p>

<img src="https://github.com/user-attachments/assets/12dfcd48-4307-4239-a7ba-27e114445790" alt="DRAConsumableCapacity" />

<p><em>Source: <a href="https://www.youtube.com/watch?v=j6zkGxrxm6o&amp;t=1007s">KubeCon NA 2025: Device Management</a></em></p>

<p><strong>Key Capabilities:</strong></p>

<ul>
<li><strong>Alpha feature</strong> introduced in Kubernetes 1.34</li>

<li>Recommended to start using from Kubernetes 1.35 (still in Alpha)</li>
</ul>

<p><strong>Core abilities:</strong></p>

<ul>
<li><strong>Allow multiple allocations</strong> over multiple resource requests</li>

<li><strong>Consumable capacity</strong>: Guaranteed resource sharing</li>
</ul>

<p><strong>Potential use cases:</strong></p>

<ul>
<li>Virtual GPU Memory Partitioning</li>

<li>Virtual NIC (vNIC) Sharing</li>

<li>Bandwidth-limited Network Allocation</li>

<li>I/O Bandwidth Smart Storage Device Sharing</li>

<li>Native Resource Request (CPU)</li>
</ul>

<p>This enables much more flexible resource sharing while maintaining topology<br />awareness.</p>

<hr />

<h2>Challenges: Device Plugin to DRA Migration</h2>

<p>Many organizations have invested heavily in Device Plugin-based solutions.<br />Migrating to DRA presents several challenges:</p>

<h3>1. Existing Device Plugin Investments</h3>

<p>Organizations may have:</p>

<ul>
<li>Custom Device Plugins with topology logic</li>

<li>Integration with monitoring and observability tools</li>

<li>Operator workflows depending on Device Plugin APIs</li>
</ul>

<h3>2. Coexistence Problems</h3>

<p>Running Device Plugin and DRA together can cause:</p>

<ul>
<li><strong>Resource conflicts</strong>: Same device managed by both systems</li>

<li><strong>Topology inconsistency</strong>: Different topology views between systems</li>

<li><strong>Scheduling confusion</strong>: Scheduler doesn&#8217;t have unified view</li>
</ul>

<h3>3. Feature Gaps</h3>

<p>Some Device Plugin features don&#8217;t have DRA equivalents yet:</p>

<ul>
<li><strong>Device health monitoring</strong>: Device Plugin has built-in health checks</li>

<li><strong>Hot-plug support</strong>: Device Plugin supports dynamic device addition</li>

<li><strong>Metrics integration</strong>: Prometheus metrics from Device Plugins</li>
</ul>

<h3>Solutions and Workarounds</h3>

<p><strong>DRA Extension Capabilities:</strong></p>

<ul>
<li>DRA drivers can implement compatibility layers</li>

<li>NVIDIA&#8217;s DRA driver supports Device Plugin migration path</li>

<li>NRI integration can bridge runtime-level gaps</li>
</ul>

<p><strong>Recommended Migration Path:</strong></p>

<ol>
<li>Deploy DRA driver alongside existing Device Plugin</li>

<li>Use node taints to partition workloads</li>

<li>Gradually migrate workloads to DRA-based resource claims</li>

<li>Phase out Device Plugin once all workloads migrated</li>
</ol>

<hr />

<h2>Related KubeCon Talks</h2>

<p>Several excellent talks from KubeCon NA 2025 cover these topics:</p>

<h3>Lightning Talk: Mind the Topology</h3>

<p><a href="https://www.youtube.com/watch?v=o5i7pTWZjfo">Mind the Topology: Smarter Scheduling for AI Workloads on Kubernetes</a><br />by Roman Baron, NVIDIA</p>

<p>Key topics:</p>

<ul>
<li>Why topology matters for AI workloads</li>

<li>NVIDIA KAI Scheduler for topology-aware scheduling</li>

<li><a href="https://github.com/NVIDIA/KAI-Scheduler">NVIDIA KAI-Scheduler</a></li>
</ul>

<h3>Device Management Deep Dive</h3>

<p><a href="https://www.youtube.com/watch?v=j6zkGxrxm6o">Deep dive into DRA and Device Plugin</a></p>

<p>Key topics:</p>

<ul>
<li>Evolution from Device Plugin to DRA</li>

<li>DRAConsumableCapacity feature</li>

<li>Multi-device topology coordination</li>
</ul>

<hr />

<h2>Best Practices for Topology-Aware Scheduling</h2>

<ol>
<li><strong>Understand your topology requirements</strong></li>
</ol>

<ul>
<li>Profile workloads to identify topology sensitivity</li>

<li>Map hardware topology (PCIe, NUMA, NVLink, RDMA)</li>
</ul>

<ol>
<li><strong>Choose the right scheduling approach</strong></li>
</ol>

<ul>
<li>Simple GPU workloads: Device Plugin + Topology Manager</li>

<li>Complex multi-device: DRA with constraints</li>

<li>Distributed training: Kueue or Volcano + DRA</li>
</ul>

<ol>
<li><strong>Label nodes with topology information</strong></li>
</ol>

<ul>
<li>Use consistent labeling scheme</li>

<li>Include rack, block, and host-level topology</li>
</ul>

<ol>
<li><strong>Test topology impact</strong></li>
</ol>

<ul>
<li>Benchmark with and without topology alignment</li>

<li>Measure latency and throughput differences</li>
</ul>

<ol>
<li><strong>Plan for migration</strong></li>
</ol>

<ul>
<li>Start with new workloads on DRA</li>

<li>Create compatibility tests</li>

<li>Document topology requirements</li>
</ul>

<hr />

<h2>Conclusion</h2>

<p>Topology-aware scheduling has evolved from a nice-to-have feature to a critical<br />requirement for AI workloads. The transition from Device Plugin to DRA<br />represents a fundamental shift in how Kubernetes manages hardware topology:</p>

<ul>
<li><strong>Device Plugin</strong>: Simple, established, but limited topology support</li>

<li><strong>DRA</strong>: Rich topology expression, multi-device coordination, future of<br />Kubernetes device management</li>
</ul>

<p>As AI workloads continue to grow in complexity, the need for sophisticated<br />topology-aware scheduling will only increase. Whether you&#8217;re using Kueue,<br />Volcano, or native Kubernetes scheduling, understanding topology and planning<br />for DRA adoption is essential for optimizing your AI infrastructure.</p>

<hr />

<h2>Resources</h2>

<h3>Projects</h3>

<ul>
<li><a href="https://github.com/kubernetes/dynamic-resource-allocation/">DRA &#8211; Dynamic Resource Allocation</a></li>

<li><a href="https://github.com/NVIDIA/k8s-dra-driver-gpu">NVIDIA DRA GPU Driver</a></li>

<li><a href="https://github.com/NVIDIA/KAI-Scheduler">NVIDIA KAI Scheduler</a></li>

<li><a href="https://github.com/kubernetes-sigs/kueue">Kueue</a></li>

<li><a href="https://github.com/volcano-sh/volcano">Volcano</a></li>

<li><a href="https://github.com/google/dranet">DRANET</a></li>

<li><a href="https://github.com/kubernetes-sigs/dra-driver-cpu">dra-driver-cpu</a></li>
</ul>

<h3>Documentation</h3>

<ul>
<li><a href="https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/">DRA Kubernetes Documentation</a></li>

<li><a href="https://cloud.google.com/compute/docs/instances/use-compact-placement-policies#verify-vm-location">GCE Topology Policies</a></li>

<li><a href="https://kubernetes.io/docs/tasks/administer-cluster/topology-manager/">Kubernetes Topology Manager</a></li>
</ul>

<h3>Videos</h3>

<ul>
<li><a href="https://www.youtube.com/watch?v=o5i7pTWZjfo">Mind the Topology &#8211; Roman Baron, NVIDIA</a></li>

<li><a href="https://www.youtube.com/watch?v=j6zkGxrxm6o">Device Management Deep Dive</a></li>
</ul>

<hr />

<p></p>
