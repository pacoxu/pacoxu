# [kubernetes 调度器： kube-scheduler 学习](https://github.com/pacoxu/pacoxu/issues/65)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2019-11-08T13:55:52+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2019/11/08/kubernetes-%e8%b0%83%e5%ba%a6%e5%99%a8%ef%bc%9a-kube-scheduler-%e5%ad%a6%e4%b9%a0/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2019-11-08`.
> Original URL: https://pacoxu.wordpress.com/2019/11/08/kubernetes-%e8%b0%83%e5%ba%a6%e5%99%a8%ef%bc%9a-kube-scheduler-%e5%ad%a6%e4%b9%a0/
<h1>官方文档</h1>
<p>Kubernetes Scheduler <a href="https://kubernetes.io/docs/concepts/scheduling/kube-scheduler/">https://kubernetes.io/docs/concepts/scheduling/kube-scheduler/</a></p>
<p>调度分两步，过滤+打分。</p>
<h2>过滤 Filtering</h2>
<ul>
<li><code>PodFitsHostPorts</code>: Checks if a Node has free ports (the network protocol kind) for the Pod ports the Pod is requesting.</li>
<li><code>PodFitsHost</code>: Checks if a Pod specifies a specific Node by it hostname.</li>
<li><code>PodFitsResources</code>: Checks if the Node has free resources (eg, CPU and Memory) to meet the requirement of the Pod.</li>
<li><code>PodMatchNodeSelector</code>: Checks if a Pod’s Node <a href="https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/">Selector</a> matches the Node’s <a href="https://kubernetes.io/docs/concepts/overview/working-with-objects/labels">label(s)</a>.</li>
<li><code>NoVolumeZoneConflict</code>: Evaluate if the <a href="https://kubernetes.io/docs/concepts/storage/volumes/">Volumes</a> that a Pod requests are available on the Node, given the failure zone restrictions for that storage.</li>
<li><code>NoDiskConflict</code>: Evaluates if a Pod can fit on a Node due to the volumes it requests, and those that are already mounted.</li>
<li><code>MaxCSIVolumeCount</code>: Decides how many <a href="https://kubernetes.io/docs/concepts/storage/volumes/#csi">CSI</a> volumes should be attached, and whether that’s over a configured limit.</li>
<li><code>CheckNodeMemoryPressure</code>: If a Node is reporting memory pressure, and there’s no configured exception, the Pod won’t be scheduled there.</li>
<li><code>CheckNodePIDPressure</code>: If a Node is reporting that process IDs are scarce, and there’s no configured exception, the Pod won’t be scheduled there.</li>
<li><code>CheckNodeDiskPressure</code>: If a Node is reporting storage pressure (a filesystem that is full or nearly full), and there’s no configured exception, the Pod won’t be scheduled there.</li>
<li><code>CheckNodeCondition</code>: Nodes can report that they have a completely full filesystem, that networking isn’t available or that kubelet is otherwise not ready to run Pods. If such a condition is set for a Node, and there’s no configured exception, the Pod won’t be scheduled there.</li>
<li><code>PodToleratesNodeTaints</code>: checks if a Pod’s <a href="https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/">tolerations</a> can tolerate the Node’s <a href="https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/">taints</a>.</li>
<li><code>CheckVolumeBinding</code>: Evaluates if a Pod can fit due to the volumes it requests. This applies for both bound and unbound <a href="https://kubernetes.io/docs/concepts/storage/persistent-volumes/">PVCs</a></li>
</ul>
<p>简单来看就是，端口可用、是否制定了hostname、资源充足、NodeSelector符合、存储卷相关检查、磁盘PID内存压力、节点状态、污点和容忍设置。</p>
<h2>打分 Scoring</h2>
<ul>
<li><code>SelectorSpreadPriority</code>: Spreads Pods across hosts, considering Pods that belonging to the same <a href="https://kubernetes.io/docs/concepts/services-networking/service/">Service</a>, <a href="https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/">StatefulSet</a> or <a href="https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/">ReplicaSet</a>.</li>
<li><code>InterPodAffinityPriority</code>: Computes a sum by iterating through the elements of weightedPodAffinityTerm and adding “weight” to the sum if the corresponding PodAffinityTerm is satisfied for that node; the node(s) with the highest sum are the most preferred.</li>
<li><code>LeastRequestedPriority</code>: Favors nodes with fewer requested resources. In other words, the more Pods that are placed on a Node, and the more resources those Pods use, the lower the ranking this policy will give.</li>
<li><code>MostRequestedPriority</code>: Favors nodes with most requested resources. This policy will fit the scheduled Pods onto the smallest number of Nodes needed to run your overall set of workloads.</li>
<li><code>RequestedToCapacityRatioPriority</code>: Creates a requestedToCapacity based ResourceAllocationPriority using default resource scoring function shape.</li>
<li><code>BalancedResourceAllocation</code>: Favors nodes with balanced resource usage.</li>
<li><code>NodePreferAvoidPodsPriority</code>: Priorities nodes according to the node annotation <code><a href="http://scheduler.alpha.kubernetes.io/preferAvoidPods">scheduler.alpha.kubernetes.io/preferAvoidPods</a></code>. You can use this to hint that two different Pods shouldn’t run on the same Node.</li>
<li><code>NodeAffinityPriority</code>: Prioritizes nodes according to node affinity scheduling preferences indicated in PreferredDuringSchedulingIgnoredDuringExecution. You can read more about this in <a href="https://kubernetes.io/docs/concepts/configuration/assign-pod-node/">Assigning Pods to Nodes</a></li>
<li><code>TaintTolerationPriority</code>: Prepares the priority list for all the nodes, based on the number of intolerable taints on the node. This policy adjusts a node’s rank taking that list into account.</li>
<li><code>ImageLocalityPriority</code>: Favors nodes that already have the <a href="https://kubernetes.io/docs/reference/glossary/?all=true#term-image">container images</a> for that Pod cached locally.</li>
<li><code>ServiceSpreadingPriority</code>: For a given Service, this policy aims to make sure that the Pods for the Service run on different nodes. It favouring scheduling onto nodes that don’t have Pods for the service already assigned there. The overall outcome is that the Service becomes more resilient to a single Node failure.</li>
<li><code>CalculateAntiAffinityPriorityMap</code>: This policy helps implement <a href="https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity">pod anti-affinity</a>.</li>
<li><code>EqualPriorityMap</code>: Gives an equal weight of one to all nodes.</li>
</ul>
<p>尽量分散调度、Pod亲和性、Node亲和性 Prefer设置、节点资源使用量、污点、已经有相应的镜像的节点加分等。</p>
<h2>大规模集群的调度速度优化</h2>
<p>Scheduler Performance Tuning： <a href="https://kubernetes.io/docs/concepts/scheduling/scheduler-perf-tuning/">https://kubernetes.io/docs/concepts/scheduling/scheduler-perf-tuning/</a></p>
<p>Percentage of Nodes to Score 就是说在集群很大的情况下，我们没必要把所有节点进行打分，1000台机器的集群，如果有500台符合调度条件，我们只要打分其中10-20台，选择一个合适的节点调度就可以了。这个打分的范围可以用百分比进行调整。用户可以根据集群规模动态调整这个值。</p>
<h2>区域分布不均的问题解决方法 Pod Topology Spread Constraints</h2>
<p><a href="https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/">https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/</a></p>

<table>
<tbody>
<tr>
<td>

<code>spec:</code>
<code>  </code><code>topologySpreadConstraints:</code>
<code>  </code><code>- maxSkew: 1</code>
<code>    </code><code>topologyKey: zone</code>
<code>    </code><code>whenUnsatisfiable: DoNotSchedule</code>
<code>    </code><code>labelSelector:</code>
<code>      </code><code>matchLabels:</code>
<code>        </code><code>foo: bar</code>

</td>
</tr>
</tbody>
</table>

<p>上面的例子表示，根据zone 进行偏移量检查，如果有两个区 A、B，每个区都有若干台机器，然后 A区2个pod、B区1个pod。</p>
<p>那么调度的时候，如果 maxSkew 为1， 那么下一个pod 一定会调度到 B区。调整 maxSkew 为2或者3，下一个pod 才有可能调度到 A区。</p>
<p>已知的一个问题：</p>
<ul>
<li>缩容的时候可能导致容器组分布不均 Scaling down a <code>Deployment</code> may result in imbalanced Pods distribution.</li>
</ul>
<h3>Pod Overhead 容器组额外开销计算</h3>
<p><a href="https://kubernetes.io/docs/concepts/configuration/pod-overhead/">https://kubernetes.io/docs/concepts/configuration/pod-overhead/</a></p>
<p>Pods have some resource overhead. In our traditional linux container (Docker) approach, the accounted overhead is limited to the infra (pause) container, but also invokes some overhead accounted to various system components including: Kubelet (control loops), Docker, kernel (various resources), fluentd (logs).</p>
<p>主要计算了 kubelet、docker、kernel 的额外开销，这个feature启动需要在 kubelet 以及 scheduler 等多处配置feature gate。</p>
<h3>kube-scheduler 启动参数</h3>
<p><a href="https://kubernetes.io/docs/reference/command-line-tools-reference/kube-scheduler/">https://kubernetes.io/docs/reference/command-line-tools-reference/kube-scheduler/</a></p>
<h3>此外 Kubernetes 支持多个 scheduler，可以在 pod 上制定调度器</h3>
<p><a href="https://kubernetes.io/docs/tasks/administer-cluster/configure-multiple-schedulers/">https://kubernetes.io/docs/tasks/administer-cluster/configure-multiple-schedulers/</a></p>
<p>如果default 调度器不符合您的调度需求，可以自己实现调度器，并在集群内配置你的调度器，或者配置多个调度器，默认情况用 default-scheduler，特定的一些 pod 通过您定制的 scheduler 进行调度。</p>
<h3>Kubernetes 原生的调度能力与扩展能力</h3>
<p>基本的调度策略： 先过滤调度条件找到合适的主机列表，然后进行打分选择最高分。</p>
<p>下面是一个案例，案例来源 <a href="https://itnext.io/keep-you-kubernetes-cluster-balanced-the-secret-to-high-availability-17edf60d9cb7">https://itnext.io/keep-you-kubernetes-cluster-balanced-the-secret-to-high-availability-17edf60d9cb7</a> 强烈推荐</p>
<p>&nbsp;</p>
<h1>调度优化的开源项目</h1>
<p><a href="https://github.com/topics/k8s-sig-scheduling">https://github.com/topics/k8s-sig-scheduling</a> 目前有三个调度相关的项目： <a href="https://github.com/kubernetes-sigs/poseidon">poseidon</a> 、 <a href="https://github.com/kubernetes-sigs/kube-batch">kube-batch</a> 、<a href="https://github.com/kubernetes-sigs/descheduler">descheduler</a>。 还有个个人项目 <a href="https://github.com/better0332/resbalancer">resbalancer</a>。</p>
<p>他们的适用场景各不相同，kube-batch 是批量调度场景，descheduler 是再次平衡调度类似二次平衡，poseidon 试图通过网络流量的数据影响调度让调度更合理。</p>
<h2>Descheduler</h2>
<p>Descheduler 的出现就是为了解决 Kubernetes 自身调度（一次性调度）不足的问题。它以定时任务方式运行，根据已实现的策略，重新去平衡 pod 在集群中的分布。</p>
<p>这个重新调度的任务可以作为 Kubernetes Job 执行，比如我们认为业务流量在凌晨2点最小，可以选择在这个时间点执行这个 Job，比如每周运行一次，保证集群的调度始终保持一个比较平均的效果。或者在上线日之后的几个小时进行 Descheduler。</p>
<p>类似的项目还有 <a href="https://github.com/pusher/k8s-spot-rescheduler">https://github.com/pusher/k8s-spot-rescheduler</a>， 该项目主要做的事情是在 AWS 的 kuber 集群中，把压力较大的节点上的 pod 重新调度到新的一组节点上，大概相当于给两组节点打上label，从一组重新调度到新的一组label上。</p>
<h2>Kube-Batch</h2>
<p>面向机器学习 / 大数据 /HPC 的批调度器（batch scheduler）。kubeflow中gang scheduler的实现就使用的是kube-batch。</p>
<p><a href="https://www.jianshu.com/p/042692685cf4">https://www.jianshu.com/p/042692685cf4</a></p>
<p><img src="https://github.com/kubernetes-sigs/kube-batch/raw/master/doc/images/kube-batch.png" alt="kube-batch" /></p>
<p>在此基础上华为推出了 <a href="https://github.com/volcano-sh/scheduler">https://github.com/volcano-sh/scheduler</a></p>
<p><img src="https://github.com/volcano-sh/volcano/raw/master/docs/images/volcano-intro.png" alt="volcano" /></p>
<h2>Poseidon （alpha <a href="https://github.com/kubernetes-sigs/poseidon/releases/tag/v0.8">https://github.com/kubernetes-sigs/poseidon/releases/tag/v0.8</a> 五月份发布 alpha 版本之后没有更新，主分支上次更新时间 2019 Apr 4）</h2>
<p>Kubernetes是支持第三方调度器插件的，而Firmament本身是用C++写的，Kubernetes是用Golang写的，所以Poseidon起的是桥梁的作用，把Firmament调度器集成到Kubernetes中。</p>
<p>Firmament是基于网络流的调度程序，它使用了高效的批处理技术，即用最小费用最大流的算法来进行优化，这种优化再加上Firmament的调度策略可以达到很好的pod放置效果。</p>
<p><a href="https://zhuanlan.zhihu.com/p/35161270">https://zhuanlan.zhihu.com/p/35161270</a></p>
<p><img src="https://pic2.zhimg.com/80/v2-2ea36f4d9bfebcb53d3b763f4e64d43d_hd.jpg" /></p>
<p>如上面案例，我们此时需要 de-scheduler</p>
<p><a href="https://github.com/kubernetes-sigs/descheduler">https://github.com/kubernetes-sigs/descheduler</a></p>
