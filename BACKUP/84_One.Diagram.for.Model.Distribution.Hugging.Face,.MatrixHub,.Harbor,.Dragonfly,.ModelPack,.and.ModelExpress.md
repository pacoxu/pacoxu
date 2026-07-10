# [One Diagram for Model Distribution: Hugging Face, MatrixHub, Harbor, Dragonfly, ModelPack, and ModelExpress](https://github.com/pacoxu/pacoxu/issues/84)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2026-04-28T17:57:47+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2026/04/28/one-diagram-for-model-distribution-hugging-face-matrixhub-harbor-dragonfly-modelpack-and-modelexpress/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2026-04-28`.
> Original URL: https://pacoxu.wordpress.com/2026/04/28/one-diagram-for-model-distribution-hugging-face-matrixhub-harbor-dragonfly-modelpack-and-modelexpress/
<p>This page puts several frequently mixed-up projects on a single diagram. The goal is to separate the&nbsp;<strong>model source</strong>,&nbsp;<strong>private registry</strong>,&nbsp;<strong>cluster distribution</strong>, and&nbsp;<strong>runtime acceleration</strong>&nbsp;layers.<br /><strong>As matrixhub is not published yet, you may try <a href="https://github.com/matrixhub-ai/matrixhub/releases/tag/v0.0.2-rc.7">v0.0.2-rc.7</a>. This is a preview of matrixhub and comparison of solutions like dragonfly + ModelPack + harbor and dynamo modelexpress.</strong></p>

<h2>The Stack in One Diagram</h2>

<p>Read the Diagram by Role</p>

<p>See <a href="https://github.com/pacoxu/AI-Infra/blob/main/docs/inference/model-distribution-stack.md#the-stack-in-one-diagram">https://github.com/pacoxu/AI-Infra/blob/main/docs/inference/model-distribution-stack.md#the-stack-in-one-diagram</a> for tech details.</p>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2026/04/image-4.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2026/04/image-4.png?w=1024" alt="" /></a>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#read-the-diagram-by-role"></a></p>

<ul>
<li><strong>Provider / server view</strong>: The blue lane is the Docker image / OCI artifact path. Harbor is easiest to read here as a local Docker Hub / Distribution style private registry. The orange lane is the model distribution path, with Hugging Face, ModelScope, and MatrixHub on that side.</li>

<li><strong>Download view</strong>: MatrixHub exposes an HF-compatible pull path. Dragonfly handles node-level file distribution and can serve OCI pulls from Harbor as well as&nbsp;<code>hf://</code>&nbsp;and&nbsp;<code>modelscope://</code>&nbsp;downloads.</li>

<li><strong>End user / runtime view</strong>: Model files first land in node-local caches, then feed GPU workers. ModelExpress sits later in the path and accelerates weight reuse between workers, including cross-node GPU transfers over RDMA.</li>
</ul>

<p>Line colors also carry meaning:</p>

<ul>
<li><strong>Orange links</strong>: HF-compatible or public model hub download paths</li>

<li><strong>Blue links</strong>: OCI pull paths</li>

<li><strong>Grey node-to-node links</strong>: Dragonfly node-level file chunk propagation</li>

<li><strong>Green GPU-to-GPU links</strong>: runtime weight sharing paths relevant to ModelExpress</li>
</ul>

<h2>Focused Reference Diagrams<a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#focused-reference-diagrams"></a></h2>

<p>1. Dragonfly path: Harbor plus public model hubs</p>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2026/04/image.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2026/04/image.png?w=1024" alt="" /></a>

<p>2. MatrixHub path: private Hugging Face style access</p>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#2-matrixhub-path-private-hugging-face-style-access"></a></p>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2026/04/image-1.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2026/04/image-1.png?w=1020" alt="" /></a>

<p>3. ModelExpress path: runtime weight sharing after initial pull （<strong>not quite familiar with this, correct me if I am wrong</strong>）</p>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#3-modelexpress-path-runtime-weight-sharing-after-initial-pull"></a></p>

<a href="https://pacoxu.wordpress.com/wp-content/uploads/2026/04/image-2.png"><img src="https://pacoxu.wordpress.com/wp-content/uploads/2026/04/image-2.png?w=1024" alt="" /></a>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#one-diagram-for-model-distribution-hugging-face-matrixhub-harbor-dragonfly-modelpack-and-modelexpress"></a></p>

<h2>Read the Diagram from Left to Right<a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#read-the-diagram-from-left-to-right"></a></h2>

<h3>1. Hugging Face<a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#1-hugging-face"></a></h3>

<p>Hugging Face is the public upstream model hub. It is the default source for many training and inference workflows using&nbsp;<code>huggingface_hub</code>,&nbsp;<code>transformers</code>,&nbsp;<code>vLLM</code>, and similar clients.</p>

<h3>2. Private Hugging Face<a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#2-private-hugging-face"></a></h3>

<p>Private Hugging Face is a&nbsp;<strong>target state</strong>, not a single product. It means:</p>

<ul>
<li>private model hosting</li>

<li>access control and governance</li>

<li>low-friction compatibility with existing HF-style workflows</li>

<li>predictable distribution inside enterprise or air-gapped environments</li>
</ul>

<h3>3. MatrixHub<a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#3-matrixhub"></a></h3>

<p>MatrixHub is the most direct path to that target state in this stack. It acts as an&nbsp;<strong>HF-compatible private hub</strong>, so teams can keep the Hugging Face interaction model while moving to a governed internal endpoint.</p>

<p>In practice, MatrixHub is the layer for:</p>

<ul>
<li>private model registry and lifecycle governance</li>

<li>transparent HF proxy behavior</li>

<li>on-demand caching from public Hugging Face</li>

<li>multi-region or air-gapped distribution workflows</li>
</ul>

<h3>4. ModelPack + Harbor + Dragonfly<a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#4-modelpack--harbor--dragonfly"></a></h3>

<p>This path is different. It is&nbsp;<strong>OCI-first</strong>, not HF-first.</p>

<ul>
<li><code>ModelPack</code>&nbsp;provides a packaging/spec path for OCI-based model artifacts.</li>

<li><code>Harbor</code>&nbsp;provides the private OCI registry, including enterprise governance features such as RBAC, signing, replication, and retention. A useful mental model is to treat it as an enterprise-local Docker Hub / Distribution style system with stronger management features.</li>

<li><code>Dragonfly</code>&nbsp;accelerates distribution from the registry to nodes using preheat and P2P transfer patterns.</li>
</ul>

<p>This stack is a strong answer to&nbsp;<strong>private model artifact management</strong>, but it does not by itself provide a native Hugging Face-compatible endpoint.</p>

<h3>5. ModelExpress</h3>

<p>ModelExpress sits later in the path. It is not the primary model hub. Its main job is&nbsp;<strong>runtime weight movement and cold-start reduction inside the cluster</strong>.<a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#5-modelexpress"></a></p>

<p>That usually means:</p>

<ul>
<li>coordinating cache usage in the inference cluster</li>

<li>reducing repeated model pulls and loads</li>

<li>enabling worker-to-worker transfer</li>

<li>accelerating the last mile from storage or cache toward serving workers</li>
</ul>

<p>The official documentation focuses on&nbsp;<strong>in-cluster multi-node coordination</strong>&nbsp;rather than a global multi-cluster control plane.</p>

<h2>The Most Common Architecture Patterns<a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#the-most-common-architecture-patterns"></a></h2>

<h3>Pattern A: Public Hugging Face<a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#pattern-a-public-hugging-face"></a></h3>

<p>Use this when convenience matters more than control.</p>

<p><code>Clients -&gt; Hugging Face</code></p>

<p>Tradeoff:</p>

<ul>
<li>simplest workflow</li>

<li>least governance</li>

<li>repeated public downloads</li>

<li>weak fit for air-gapped or regulated environments</li>
</ul>

<h3>Pattern B: Private Hugging Face with MatrixHub</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#pattern-b-private-hugging-face-with-matrixhub"></a></p>

<p>Use this when existing HF workflows should remain almost unchanged.</p>

<p><code>Clients -&gt; MatrixHub -&gt; Hugging Face or private storage</code></p>

<p>Tradeoff:</p>

<ul>
<li>lowest migration cost for HF-first teams</li>

<li>strong fit for internal mirroring and governance</li>

<li>less aligned with OCI-first platform standardization than Harbor</li>
</ul>

<h3>Pattern C: Private Model Registry with Harbor + ModelPack + Dragonfly</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#pattern-c-private-model-registry-with-harbor--modelpack--dragonfly"></a></p>

<p>Use this when the platform is already centered on OCI artifacts and Kubernetes.</p>

<p><code>Build/package -&gt; ModelPack -&gt; Harbor -&gt; Dragonfly -&gt; cluster nodes</code></p>

<p>Tradeoff:</p>

<ul>
<li>strong standardization and enterprise controls</li>

<li>clean fit for OCI-native platform teams</li>

<li>more workflow translation if users expect native HF semantics</li>
</ul>

<h3>Pattern D: MatrixHub + ModelExpress</h3>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#pattern-d-matrixhub--modelexpress"></a></p>

<p>Use this when you need both&nbsp;<strong>private Hugging Face-style access</strong>&nbsp;and&nbsp;<strong>faster cluster runtime loading</strong>.</p>

<p><code>Clients -&gt; MatrixHub -&gt; cluster cache/source -&gt; ModelExpress -&gt; workers</code></p>

<p>Division of responsibility:</p>

<ul>
<li><code>MatrixHub</code>&nbsp;is the upstream system of record and governed distribution layer.</li>

<li><code>ModelExpress</code>&nbsp;is the in-cluster runtime acceleration layer.</li>
</ul>

<p>This is especially natural in multi-cluster environments where each cluster runs its own runtime acceleration path while a shared upstream model source keeps versions and access policies consistent.</p>

<h2>Quick Positioning Table</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#quick-positioning-table"></a></p>

<table><thead><tr><th>Component</th><th>Primary layer</th><th>Best for</th></tr></thead><tbody><tr><td>Hugging Face</td><td>Public upstream hub</td><td>Public model discovery and default client workflows</td></tr><tr><td>Private Hugging Face</td><td>Capability / target state</td><td>Internal HF-like experience</td></tr><tr><td>MatrixHub</td><td>Private model hub</td><td>HF-compatible internal distribution and governance</td></tr><tr><td>ModelPack</td><td>Packaging/spec</td><td>OCI-based model artifact definition</td></tr><tr><td>Harbor</td><td>Private registry</td><td>OCI artifact governance and replication</td></tr><tr><td>Dragonfly</td><td>Cluster distribution</td><td>Large-scale node-level pull acceleration</td></tr><tr><td>ModelExpress</td><td>Runtime acceleration</td><td>In-cluster cold-start and weight transfer optimization</td></tr></tbody></table>

<h2>Practical Rule of Thumb</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#practical-rule-of-thumb"></a></p>

<ul>
<li>If the question is&nbsp;<strong>&#8220;where should models live and be governed?&#8221;</strong>, think&nbsp;<code>MatrixHub</code>&nbsp;or&nbsp;<code>Harbor</code>.</li>

<li>If the question is&nbsp;<strong>&#8220;do we want HF-compatible developer experience or OCI-first artifact workflows?&#8221;</strong>, choose between&nbsp;<code>MatrixHub</code>&nbsp;and&nbsp;<code>Harbor + ModelPack</code>.</li>

<li>If the question is&nbsp;<strong>&#8220;how do we reduce cluster cold-start and repeated weight movement?&#8221;</strong>, think&nbsp;<code>Dragonfly</code>&nbsp;and&nbsp;<code>ModelExpress</code>.</li>

<li>If the question is&nbsp;<strong>&#8220;how do we keep HF-like access while improving last-mile runtime loading?&#8221;</strong>, combine&nbsp;<code>MatrixHub</code>&nbsp;with&nbsp;<code>ModelExpress</code>.</li>
</ul>

<h2>References</h2>

<p><a href="https://github.com/pacoxu/AI-Infra/blob/91bf9f23649ae943bbcbc3de95c0fbb8c669e7d0/docs/inference/model-distribution-stack.md#references"></a></p>

<ul>
<li><a href="https://github.com/matrixhub-ai/matrixhub">MatrixHub</a></li>

<li><a href="https://github.com/ai-dynamo/modelexpress">ModelExpress</a></li>

<li><a href="https://goharbor.io/">Harbor</a></li>

<li><a href="https://d7y.io/">Dragonfly</a></li>

<li><a href="https://modelpack.org/">ModelPack</a></li>

<li><a href="https://huggingface.co/">Hugging Face</a></li>
</ul>
