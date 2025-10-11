---
layout: page
title: "IOSD: Improved Open-vocabulary Segmentation with Diffusion Models"
description: Enhanced Grounded Diffusion for open-vocabulary segmentation using Stable Diffusion XL.
img: /assets/img/iosd/teaser.png
category: work
---

<div class="row">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid loading="eager" path="assets/img/iosd/visual_encoder.png" title="Visual encoder design" class="img-fluid rounded z-depth-1" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid loading="eager" path="assets/img/iosd/fusion_module.png" title="Visual–text fusion module" class="img-fluid rounded z-depth-1" %}
  </div>
</div>

<div class="caption">
  Left: The visual encoder extracts multi-scale latent features from all U-Net layers.  
  Right: The transformer-based fusion module aligns visual and textual representations for open-vocabulary segmentation.
</div>

---

### Project Overview
**IOSD (Improved Open-vocabulary Segmentation with Diffusion Models)** introduces a novel diffusion-based framework for open-vocabulary semantic segmentation.  
Built upon *Grounded Diffusion* and *Stable Diffusion XL*, IOSD enhances segmentation quality and text–image alignment by:

- Extracting multi-scale latent features from all U-Net layers  
- Introducing a transformer-based visual–text fusion module  
- Using prompt engineering and mask filtering for better generalization  

IOSD achieves **state-of-the-art zero-shot segmentation** performance on COCO and PASCAL VOC datasets, enabling models to understand and segment arbitrary visual concepts described in text.

---

<div class="row justify-content-sm-center">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid loading="eager" path="assets/img/iosd/compare.png" title="Comparison with Grounded Diffusion" class="img-fluid rounded z-depth-1" %}
  </div>
</div>
<div class="caption">
  Example segmentation results. IOSD accurately detects unseen categories such as “red envelope” and “lion dance,” demonstrating strong generalization in open-vocabulary scenarios.
</div>

---

### Implementation Details

<div class="row">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/iosd/model_architecture.png" title="IOSD model architecture" class="img-fluid rounded z-depth-1" %}
  </div>
</div>
<div class="caption">
  Overall architecture of IOSD. The model integrates multi-layer U-Net features with a transformer-based fusion head to enable fine-grained open-vocabulary semantic segmentation.
</div>


- **Backbone:** Stable Diffusion XL-Turbo (base-1.0)  
- **Training framework:** MMDetection + Grounded-SAM integration  
- **Datasets:** PASCAL VOC 2012, COCO 2017  
- **Metrics:** mIoU, PQ, ZS-mIoU (zero-shot mean IoU)

---
<h3>Quantitative Results</h3>

<p>
We evaluate models using mIoU scores on three class splits. For each class, 50 images are generated and evaluated using <code>mmdetection</code> for ground-truth segmentation masks. Training follows the DSF setting (see Ablation Table for details).
</p>

<div class="table-responsive">
  <table class="table table-sm table-bordered text-center align-middle">
    <thead class="table-light">
      <tr>
        <th rowspan="2">Model</th>
        <th rowspan="2">Class Split</th>
        <th colspan="2">PASCAL (mIoU ↑)</th>
        <th colspan="2">COCO (mIoU ↑)</th>
      </tr>
      <tr>
        <th>Seen</th>
        <th>Unseen</th>
        <th>Seen</th>
        <th>Unseen</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td rowspan="4">DAAM<sup>[1]</sup></td>
        <td>Split 1</td><td>61.66</td><td>75.63</td><td>62.25</td><td>55.56</td>
      </tr>
      <tr>
        <td>Split 2</td><td>65.75</td><td>59.25</td><td>60.08</td><td>65.55</td>
      </tr>
      <tr>
        <td>Split 3</td><td>67.11</td><td>53.82</td><td>62.81</td><td>52.48</td>
      </tr>
      <tr class="table-secondary fw-bold">
        <td>Average</td><td>64.84</td><td>62.90</td><td>61.71</td><td>57.76</td>
      </tr>
      <tr>
        <td rowspan="4">GD<sup>[2]</sup></td>
        <td>Split 1</td><td>90.16</td><td>83.19</td><td>83.35</td><td>76.81</td>
      </tr>
      <tr>
        <td>Split 2</td><td>90.08</td><td>86.19</td><td>82.83</td><td>74.93</td>
      </tr>
      <tr>
        <td>Split 3</td><td>90.67</td><td>79.86</td><td>84.85</td><td>67.89</td>
      </tr>
      <tr class="table-secondary fw-bold">
        <td>Average</td><td>90.30</td><td>83.08</td><td>83.68</td><td>73.21</td>
      </tr>
      <tr>
        <td rowspan="4"><b>IOSD (Ours)</b></td>
        <td>Split 1</td><td>92.54</td><td>84.76</td><td>90.79</td><td>88.04</td>
      </tr>
      <tr>
        <td>Split 2</td><td>92.18</td><td>88.18</td><td>90.81</td><td>79.34</td>
      </tr>
      <tr>
        <td>Split 3</td><td>93.29</td><td>80.71</td><td>91.49</td><td>83.03</td>
      </tr>
      <tr class="table-secondary fw-bold">
        <td>Average</td><td><b>92.67</b></td><td><b>84.55</b></td><td><b>91.03</b></td><td><b>83.47</b></td>
      </tr>
    </tbody>
  </table>
</div>

<p class="text-muted small">
<sup>[1]</sup> Tang et al., <i>DAAM: Diffusion Attention Attribution Maps</i>, 2022.  
<sup>[2]</sup> Li et al., <i>Grounded Diffusion for Open-Vocabulary Segmentation</i>, 2023.
</p>