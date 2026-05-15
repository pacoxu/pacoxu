# [Introducing llmaz: Easy, advanced inference platform for large language models on Kubernetes](https://github.com/pacoxu/pacoxu/issues/74)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2025-04-23T15:28:06+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2025/04/23/introducing-llmaz-easy-advanced-inference-platform-for-large-language-models-on-kubernetes/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2025-04-23`.
> Original URL: https://pacoxu.wordpress.com/2025/04/23/introducing-llmaz-easy-advanced-inference-platform-for-large-language-models-on-kubernetes/
<p>InftyAI&#8217;s <a href="https://github.com/InftyAI/llmaz">llmaz</a> is an advanced inference platform designed to streamline the deployment and management of large language models (LLMs) on Kubernetes. By integrating state-of-the-art inference backends, llmaz brings cutting-edge research to the cloud, offering a production-ready solution for LLMs.</p>

<p><strong>Key Features of llmaz:</strong></p>

<ul>
<li><strong>Kubernetes Integration for easy to use:</strong> deploy and manage LLMs within Kubernetes clusters, leveraging Kubernetes&#8217; robust orchestration capabilities.</li>

<li><strong>Advanced Inference Backends:</strong> Utilize state-of-the-art inference backends to ensure efficient and scalable model serving.</li>

<li><strong>Production-Ready:</strong> Designed for production environments, llmaz offers reliability and performance for enterprise applications.</li>
</ul>

<p><strong>The deployment of a model is quite simple in llmaz.</strong></p>

<p>Here&#8217;s a toy example for deploying <code>deepseek-ai/DeepSeek-R1</code>, all you need to do is to apply a Model and a Playground.</p>

<table><tbody><tr><td>apiVersion: llmaz.io/v1alpha1<br />kind: OpenModel<br />metadata:<br />  name: opt-125m<br />spec:<br />  familyName: opt<br />  source:<br />    modelHub:<br />      modelID: deepseek-ai/DeepSeek-R1<br />  inferenceConfig:<br />    flavors:<br />      &#8211; name: default # Configure GPU type<br />        requests:<br />          nvidia.com/gpu: 1<br />&#8212;<br />apiVersion: inference.llmaz.io/v1alpha1<br />kind: Playground<br />metadata:<br />  name: opt-125m<br />spec:<br />  replicas: 1<br />  modelClaim:<br />    modelName: opt-125m<br /></td></tr></tbody></table>

<p><strong>Latest Release: </strong><a href="https://github.com/InftyAI/llmaz/releases/tag/v0.1.3"><strong>v0.1.3</strong></a></p>

<p>The latest release, v0.1.3, was released on April 23th, 2025. The release v0.1 includes several enhancements and bug fixes to improve the platform&#8217;s stability and performance. For detailed information on the changes introduced in this release, please refer to the<a href="https://github.com/InftyAI/llmaz/releases"> release notes</a>.</p>

<p><strong>Integrations</strong></p>

<img src="https://lh7-rt.googleusercontent.com/docsz/AD_4nXdkVjQtoA3akViMOywSbTa8VGZt9N4vizAbA_jpVzNUGICJbs8SJzs1wJBj6u7gklVk65WEJ8KCagCGHpNbiZXdFIi_hLMQxHbNPEE4sIDpeG4yh8mWUHmLQ5iHg8vp78aKbiuubA?key=AKcJPkSicniKo787HqxLHlw8" alt="" />

<p>Broad Backends Support: &nbsp;llmaz supports a wide range of advanced inference backends for different scenarios, like <a href="https://github.com/vllm-project/vllm">vLLM</a>, <a href="https://github.com/huggingface/text-generation-inference">Text-Generation-Inference</a>, <a href="https://github.com/sgl-project/sglang">SGLang</a>, <a href="https://github.com/ggerganov/llama.cpp">llama.cpp</a>. Find the full list of supported backends <a href="https://github.com/InftyAI/llmaz/blob/main/docs/support-backends.md">here</a>.</p>

<p>llmaz supports a wide range of model providers, such as <a href="https://huggingface.co/">HuggingFace</a>, <a href="https://www.modelscope.cn/">ModelScope</a>, ObjectStores.</p>

<p><strong>AI Gateway Support</strong>: Offering capabilities like token-based rate limiting, model routing with the integration of <a href="https://aigateway.envoyproxy.io/">Envoy AI Gateway</a>.<br /><strong>Build-in ChatUI</strong>: Out-of-the-box chatbot support with the integration of <a href="https://github.com/open-webui/open-webui">Open WebUI</a>, offering capacities like function call, RAG, web search and more, see configurations <a href="https://github.com/InftyAI/llmaz/blob/main/docs/open-webui.md">here</a>. </p>

<p>llmaz, serving as an easy to use and advanced inference platform, uses <a href="https://github.com/kubernetes-sigs/lws/tree/main/docs/adoption#integrations">LeaderWorkerSet</a> as the underlying workload to support both single-host and multi-host inference scenarios.</p>

<p></p>

<p>llmaz supports horizontal scaling with <a href="https://github.com/InftyAI/llmaz/blob/main/docs/examples/hpa/README.md">HPA</a> by default and will integrate with autoscaling components like <a href="https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler">Cluster-Autoscaler</a> or <a href="https://github.com/kubernetes-sigs/karpenter">Karpenter</a> for smart scaling across different clouds.</p>

<p><strong>About the Founder: Kante Yin</strong></p>

<p>Kante Yin is a prominent figure in the Kubernetes community, serving as a SIG Scheduling Approver and a top committer of LWS and Kueue. His contributions to Kubernetes scheduling and workload management have been instrumental in advancing cloud-native technologies. Kante&#8217;s expertise and leadership continue to drive innovation in the Kubernetes ecosystem.</p>

<p>Compared to other inference platforms, llmaz stands out with its <strong>extensionable cloud-native design</strong>, making it incredibly <strong>lightweight</strong> and efficient. Its architecture is optimized for scalability and resource efficiency, enabling seamless integration into modern cloud environments while maintaining high performance.</p>

<h2>OSPP 2025 (Open Source Software Supply)</h2>

<p>The Open Source Promotion Plan is a summer program organized by the Open Source Software Supply Chain Promotion Plan of the Institute of Software Chinese Academy of Sciences in 2020. It aims to encourage university students to actively participate in the development and maintenance of open source software, cultivate and discover more outstanding developers, promote the vigorous development of excellent open source software communities, and assist in the construction of open source software supply chains.</p>

<p>llmaz has 2 projects in OSPP 2025. Student Registration and Application: May 9 &#8211; June 9. Welcome to our community.</p>

<ol>
<li><a href="https://summer-ospp.ac.cn/org/prodetail/257c80102?lang=zh&amp;list=pro">KEDA-based Serverless Elastic Scaling for llmaz</a></li>

<li><a href="https://summer-ospp.ac.cn/org/prodetail/257c80106?lang=zh&amp;list=pro">Enabling Efficient Model and Container Image Distribution in LLMaz with Dragonfly</a></li>
</ol>

<p>For more information about llmaz and its features, visit the<a href="https://github.com/InftyAI/llmaz"> GitHub repository</a>.</p>

<p></p>
