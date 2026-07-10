# [The Shift to cgroups v2 in Kubernetes: What You Need to Know](https://github.com/pacoxu/pacoxu/issues/75)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2025-10-21T13:08:18+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2025/10/21/the-shift-to-cgroups-v2-in-kubernetes-what-you-need-to-know/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2025-10-21`.
> Original URL: https://pacoxu.wordpress.com/2025/10/21/the-shift-to-cgroups-v2-in-kubernetes-what-you-need-to-know/
<blockquote>
<p>As v1.35 will announce the cgroup v1 deprecation, kubelet will fail on cgroup v1 with default configuration.  <code>FailCgroupV1</code> will be set to true by default. See more in coming blog <a href="https://github.com/kubernetes/website/pull/52814">https://github.com/kubernetes/website/pull/52814</a>. Blow is what I wrote after cgroup v1 was announced to enter maintenance mode. As I linked a lot and can not finish is pretty complete, I stopped update <a href="https://github.com/kubernetes/website/pull/47342">https://github.com/kubernetes/website/pull/47342</a>. Just publish it here for users who want to know more about why we should shift from cgroup v1 to v2 and the difference. </p>
</blockquote>

<p><code>cgroups</code>&nbsp;(control groups) are a Linux kernel feature used for managing system resources. Kubernetes uses cgroups to allocate resources like CPU and memory to containers, ensuring that applications run smoothly without interfering with each other. With the release of Kubernetes v1.31, cgroups v1 has been moved into [maintenance mode]/blog/2024/08/14/kubernetes-1-31-moving-cgroup-v1-support-maintenance-mode/). For cgroups v2, it graduated in v1.25 2 years ago.</p>

<p>Top FAQs are why we should migrate, what&#8217;s the benifits and lost, and what needs to be noticed when using cgroups v2.</p>

<h2>cgroups v1 problem, and solutions in cgroups v2</h2>

<p><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/content/en/blog/_posts/2024-11-10-migrate-cgroup-v2.md#cgroups-v1-problem-and-solutions-in-cgroups-v2"></a></p>

<p>cgroups v1 and cgroups official doc can be found in</p>

<ul>
<li><a href="https://www.kernel.org/doc/Documentation/cgroup-v1/">v1 doc</a></li>

<li><a href="https://www.kernel.org/doc/Documentation/cgroup-v2.txt">v2 doc</a></li>
</ul>

<p>Let&#8217;s enumerate some known issues.</p>

<h3>active_file memory is not considered as available memory</h3>

<p><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/content/en/blog/_posts/2024-11-10-migrate-cgroup-v2.md#active_file-memory-is-not-considered-as-available-memory"></a></p>

<p>There is&nbsp;<a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/docs/concepts/scheduling-eviction/node-pressure-eviction/#active-file-memory-is-not-considered-as-available-memory">a known issue</a>&nbsp;of page cache:&nbsp;<a href="https://github.com/kubernetes/kubernetes/issues/43916">#43916</a>.</p>

<ul>
<li>In cgroups v1, we have no native solutions. Workarounds are setting larger memory limit for Pods or using some external projects to drop cache or throttling memory allocating when memory is beyond a threshold.</li>

<li>In cgroups v2, we can use&nbsp;<code>memory.high</code>&nbsp;to throttle.</li>
</ul>

<p>Support for Memory QoS was initially added in Kubernetes v1.22, and later some limitations around the formula for calculating&nbsp;<code>memory.high</code>&nbsp;were identified. These limitations are addressed in Kubernetes v1.27.</p>

<p>However, until v1.31, the feature gate is still alpha due to another known issue that application pod may be hanging forever due to heavy memory reclaiming.</p>

<h3>Container aware OOM killer and better OOM handling strategies</h3>

<p><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/content/en/blog/_posts/2024-11-10-migrate-cgroup-v2.md#container-aware-oom-killer-and-better-oom-handling-strategies"></a></p>

<p>In cgroups v2, one process of a multi-processes Pod could be killed by the OOM killer. In this case, Pod has to use&nbsp;<a href="https://github.com/void-linux/runit">runit</a>&nbsp;or supervisord to manage multi processes lifecycle.</p>

<p>cgroups v2 uses&nbsp;<code>cgroup.kill</code>&nbsp;file. Writing “1” to the file causes the cgroups and all descendant cgroups to be killed. This means that all processes located in the affected cgroup tree will be killed via SIGKILL. Pod may run multiple processes, and all processes can be killed simultaneously.</p>

<p>As mentioned above, cgroups v2&nbsp;<code>memory.high</code>&nbsp;can throttle the new memory allocation and cgroups can be aware of the OOM earsiler. Besides, PSI can also help to know the memory load.&nbsp;<a href="https://github.com/facebookincubator/oomd">oomd</a>&nbsp;is a good example using PSI to implement a userspace out-of-memory killer.</p>

<h3>Rootless support</h3>

<p><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/content/en/blog/_posts/2024-11-10-migrate-cgroup-v2.md#rootless-support"></a></p>

<p>In cgroups v1, delegating cgroups v1 controllers to less privileged containers may be dangerous.</p>

<p>Unlike cgroups v1, cgroups v2 officially supports delegation. Most Rootless Containers implementations rely on systemd for delegating v2 controllers to non-root users.</p>

<p>User Namespace minimal kernel version is 6.5, according to&nbsp;<a href="https://github.com/kubernetes/enhancements/blob/master/keps/sig-node/127-user-namespaces/README.md">KEP-127</a>.</p>

<h3>What&#8217;s more?</h3>

<p><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/content/en/blog/_posts/2024-11-10-migrate-cgroup-v2.md#whats-more"></a></p>

<ol>
<li>eBPF stories:
<ul>
<li>In cgroups v1, the device access control are defined in the static configuration/.</li>

<li>cgroups v2 device controller has no interface files and is implemented on top of cgroup BPF.</li>

<li>Cilium will automatically mount cgroups v2 filesystem required to attach BPF cgroup programs by default at the path /run/cilium/cgroupv2 .</li>
</ul>
</li>

<li>PSI is planned in a future release&nbsp;<a href="https://github.com/kubernetes/enhancements/issues/4205">KEP-4205</a>, but pending due to runc 1.2.0 release delay.</li>

<li>monitoring tools support, like&nbsp;<a href="https://github.com/google/cadvisor/">Cadvisor</a>. Currently, cgroups v2 features are not fully-supported yet.</li>
</ol>

<h2>Adopting cgroup version 2</h2>

<p><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/content/en/blog/_posts/2024-11-10-migrate-cgroup-v2.md#adopting-cgroup-version-2"></a></p>

<h3>Requirements</h3>

<p><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/content/en/blog/_posts/2024-11-10-migrate-cgroup-v2.md#requirements"></a></p>

<p>Here&#8217;s what you need to use cgroup v2 with Kubernetes. First up, you need to be using a version of Kubernetes with support for v2 cgroup management; that&#8217;s been stable since Kubernetes v1.25 and all supported Kubernetes releases include this support.</p>

<ul>
<li>OS distribution enables cgroups v2</li>

<li>Linux Kernel version is 5.8 or later</li>

<li>Container runtime supports cgroups v2. For example:
<ul>
<li>containerd v1.4 or later (at the time of writing, containerd releases v1.6 and later are within that project&#8217;s support period)</li>

<li>CRI-O v1.20 or later</li>
</ul>
</li>

<li>The kubelet and the container runtime are configured to use the systemd cgroup driver</li>
</ul>

<h4>kernel updates around cgroups v2</h4>

<p><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/content/en/blog/_posts/2024-11-10-migrate-cgroup-v2.md#kernel-updates-around-cgroups-v2"></a></p>

<p>cgroups v2 first appeared in Linux Kernel 4.5 in 2016.</p>

<ul>
<li>In Linux 4.5, cgroups v2&nbsp;<code>io</code>,&nbsp;<code>memory</code>&nbsp;&amp;&nbsp;<code>pid</code>&nbsp;cgroups management were supported.</li>

<li>Linux 4.15 added support for cgroups v2&nbsp;<code>cpu</code>&nbsp;management</li>

<li><a href="https://docs.kernel.org/accounting/psi.html">Pressure Stall Information</a>&nbsp;(PSI) support began with Linux 4.20.</li>

<li>The Kubernetes project does not recommend using cgroups v2 with a Linux kernel older than 5.2 due to lack of cgroup-level task freezer support.</li>

<li>In Kubernetes, 5.8 is the minimal kernel version for cgroups v2 as root&nbsp;<code>cpu.stat</code>&nbsp;file on cgroupv2 was only added on kernel 5.8.</li>

<li><code>memory.peak</code>&nbsp;is added in 5.19.</li>
</ul>

<h3>Use systemd as cgroup driver</h3>

<p><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/content/en/blog/_posts/2024-11-10-migrate-cgroup-v2.md#use-systemd-as-cgroup-driver"></a></p>

<p><a href="https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/configure-cgroup-driver/">Configure the kubelet&#8217;s cgroup driver to match the container runtime cgroup driver</a>.</p>

<p>The&nbsp;<a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/docs/setup/production-environment/container-runtimes">Container runtimes</a>&nbsp;page explains that the&nbsp;<code>systemd</code>&nbsp;driver is recommended for kubeadm based setups instead of the kubelet&#8217;s default&nbsp;<code>cgroupfs</code>&nbsp;driver, because kubeadm manages the kubelet as a systemd service.</p>

<p>A minimal example of configuring the field explicitly:</p>

<pre>apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd</pre>

<p>In v1.31,&nbsp;<a href="https://github.com/kubernetes/enhancements/issues/4033">KEP-4033</a>&nbsp;is beta to extend CRI API for the kubelet to discover the cgroup driver from the container runtime. This will help installer and kubelet to autodetect</p>

<h3>Tools and commands for troubleshooting<a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/content/en/blog/_posts/2024-11-10-migrate-cgroup-v2.md#tools-and-commands-for-troubleshooting"></a></h3>

<p>Tools and commands that you should know about cgroups:</p>

<ul>
<li><code>stat -fc %T /sys/fs/cgroup/</code>: Check if cgroups v2 is enabled which will return&nbsp;<code>cgroup2fs</code></li>

<li><code>systemctl list-units kube* --type=slice</code>&nbsp;or&nbsp;<code>--type=scope</code>: List kube related units that systemd currently has in memory.</li>

<li><code>bpftool cgroup list /sys/fs/cgroup/*</code>: List all programs attached to the cgroup CGROUP.</li>

<li><code>systemd-cgls /sys/fs/cgroup/*</code>: Recursively show control group contents.</li>

<li><code>systemd-cgtop</code>: Show top control groups by their resource usage.</li>

<li><code>tree -L 2 -d /sys/fs/cgroup/kubepods.slice</code>: Show Pods&#8217; related cgroups directories.</li>
</ul>

<p>How to check if a Pod CPU or memory limit is successfully applied to the cgroup file?</p>

<ul>
<li>Kubernetes Pod Spec: check limits&nbsp;<code>spec.containers[*].resources.limits.{cpu,memory}</code>&nbsp;and requests&nbsp;<code>spec.containers[*].resources.requests.{cpu,memory}</code></li>

<li>CRI:&nbsp;<code>cpu_period</code>,&nbsp;<code>cpu_quota</code>,&nbsp;<code>cpu_shares</code>&nbsp;for CPU and&nbsp;<code>memory_limit_in_bytes</code>&nbsp;for memory limit</li>

<li>OCI Spec:&nbsp;<code>memorry.limit</code>,&nbsp;<code>cpu.shares</code>,&nbsp;<code>cpu.quota</code>,&nbsp;<code>cpu.period</code></li>

<li>Systemd Scope Unit:&nbsp;<code>CPUWeight</code>,&nbsp;<code>CPUQuotaPerSecUSec</code>,&nbsp;<code>CPUQuotaPeriodUSec</code>,&nbsp;<code>MemoryMax</code></li>

<li>Cgroupfs value:&nbsp;<code>/sys/fs/cgroup/../cpu.weight</code>,&nbsp;<code>/sys/fs/cgroup/../cpu.max</code>,&nbsp;<code>/sys/fs/cgroup/../memory.max</code></li>
</ul>

<h2>Further reading</h2>

<p><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/content/en/blog/_posts/2024-11-10-migrate-cgroup-v2.md#further-reading"></a></p>

<ul>
<li><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/blog/2024/08/15/kubernetes-1-31-moving-cgroup-v1-support-maintenance-mode">Kubernetes 1.31: Moving cgroups v1 Support into Maintenance Mode</a></li>

<li><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/docs/concepts/architecture/cgroups">cgroups v2 in Kubernetes</a></li>

<li><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/blog/2023/05/05/qos-memory-resources">Kubernetes 1.27: Quality-of-Service for Memory Resources (alpha)</a></li>

<li><a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/blog/2022/08/31/cgroupv2-ga-1-25">Kubernetes 1.25: cgroups v2 graduates to GA</a></li>

<li>KubeCon NA 2022&nbsp;<a href="https://www.youtube.com/watch?v=WxZK-UXKvXk">Cgroups V2: Before You Jump In</a>&nbsp;by Tony Gosselin &amp; Mike Tougeron, Adobe Systems</li>

<li>KubeCon NA 2022&nbsp;<a href="https://www.youtube.com/watch?v=sgyFCp1CRhA">Cgroupv2 Is Coming Soon To a Cluster Near You</a>&nbsp;&#8211; David Porter, Google &amp; Mrunal Patel, RedHat</li>

<li>KubeCon EU 2020&nbsp;<a href="https://www.youtube.com/watch?v=u8h0e84HxcE&amp;t=783s">Kubernetes On cgroups v2</a>&nbsp;by Giuseppe Scrivano, Red Hat.</li>

<li>Note, this blog will only include the basic requirments and configurations in Kubernetes components. It will not include how to enable cgroup fs in OS distributions. For migration, you can refer to&nbsp;<a href="https://github.com/pacoxu/website/blob/b1284403e0e45ec65509aa129ab9fe8b1a425d06/docs/concepts/architecture/cgroups/#migrating-cgroupv2">migrating cgroups v2</a></li>
</ul>

<p></p>
