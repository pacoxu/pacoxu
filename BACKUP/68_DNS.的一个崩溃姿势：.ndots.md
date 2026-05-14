# [DNS 的一个崩溃姿势： ndots](https://github.com/pacoxu/pacoxu/issues/68)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2022-03-19T11:29:17+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2022/03/19/dns-%e7%9a%84%e4%b8%80%e4%b8%aa%e5%b4%a9%e6%ba%83%e5%a7%bf%e5%8a%bf%ef%bc%9a-ndots/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2022-03-19`.
> Original URL: https://pacoxu.wordpress.com/2022/03/19/dns-%e7%9a%84%e4%b8%80%e4%b8%aa%e5%b4%a9%e6%ba%83%e5%a7%bf%e5%8a%bf%ef%bc%9a-ndots/
<p>下图来源：<a href="https://mrkaran.dev/posts/ndots-kubernetes/?utm_sq=gbj18v3zpx">https://mrkaran.dev/posts/ndots-kubernetes/?utm_sq=gbj18v3zpx</a>  关于 DNS 的问题还是有很多可以聊的，ndots/search 是其中之一。</p>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2022/03/image.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2022/03/image.png?w=672" alt="" /></a>

<p>在社区整理的 kubernetes 失败故事中，https://codeberg.org/hjacobs/kubernetes-failure-stories 提到了几个 CoreDNS 默认设置带来的潜在问题，其中 ndots 设置是一个比较常见的问题。在进行外部域名解析的时候，比如 abc.com， nodts=5 意味着所有的 search 都要进行，会给 dns 带来一些没必要的压力。在大量外部域名解析的场景下，建议 Pod 配置 ndots。</p>

<p>官网给出了一个手动设置ndots 的方法 <a href="https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/#pod-dns-config  ">https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/#pod-dns-config  </a></p>

<pre>apiVersion: v1
kind: Pod
metadata:
  namespace: default
  name: dns-example
spec:
  containers:
    - name: test
      image: nginx
  dnsPolicy: &quot;None&quot;
  dnsConfig:
    nameservers:
      - 1.2.3.4
    searches:
      - ns1.svc.cluster-domain.example
      - my.dns.search.suffix
    options:
      - name: ndots
        value: &quot;2&quot;
</pre>

<pre>kyverno 提供了一个策略引擎，可以默认设置 pod 的一些参数，比如 ndots。
<a href="https://kyverno.io/policies/other/add_ndots/?policytypes=Pod">https://kyverno.io/policies/other/add_ndots/?policytypes=Pod 
</a></pre>

<pre>
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: add-ndots
  annotations:
    policies.kyverno.io/title: Add ndots
    policies.kyverno.io/category: Sample
    policies.kyverno.io/subject: Pod
    policies.kyverno.io/description: &gt;-
      The ndots value controls where DNS lookups are first performed in a cluster
      and needs to be set to a lower value than the default of 5 in some cases.
      This policy mutates all Pods to add the ndots option with a value of 1.      
spec:
  background: false
  rules:
  - name: add-ndots
    match:
      resources:
        kinds:
        - Pod
    mutate:
      patchStrategicMerge:
        spec:
          dnsConfig:
            options:
              - name: ndots
                value: &quot;1&quot;</pre>

<p>关于 DNS，这里推荐两期 TGIK 的内容&nbsp;</p>

<p><a href="https://github.com/vmware-tanzu/tgik/blob/master/episodes/122/README.md">https://github.com/vmware-tanzu/tgik/blob/master/episodes/122/README.md</a></p>

<p><a href="https://github.com/vmware-tanzu/tgik/blob/master/episodes/147/README.md">https://github.com/vmware-tanzu/tgik/blob/master/episodes/147/README.md</a></p>

<p>有兴趣可以看下。</p>
