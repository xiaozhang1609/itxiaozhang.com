---
title: 编程案例：摄影照片展示网站纯前端实现（HTML、CSS、JS）
permalink: /spa-photography-gallery/
date: 2025-03-30 16:54:12
description: 「视界捕手」是一个单页面应用（SPA），用于展示摄影照片，基于JavaScript动态加载图片内容，使用CSS网格布局实现响应式展示。页面切换时，通过淡入淡出动画实现平滑过渡，所有交互均无需重新加载页面。
category:
- 编程案例
tags:
- 前端
- html
- css
- js
- 编程
---

> 原文地址：<https://itxiaozhang.com/spa-photography-gallery/>  
> 本文配合视频食用效果最佳，视频版本在文章末尾。

## 需求分析  

「视界捕手」是一个单页面应用（SPA），用于展示摄影照片，主要需求包括：  

1. **动态照片展示**：用户可浏览高质量摄影作品，页面采用CSS网格布局，支持响应式展示。  
2. **无刷新分类筛选**：点击分类标签后，页面内容动态更新，无需重新加载。  
3. **流畅的交互体验**：页面切换采用淡入淡出动画，提升视觉效果。  
4. **纯前端实现**：利用HTML、CSS和JavaScript完成所有功能，无需后端支持。  

## 核心功能  

1. **图片动态加载**：通过JavaScript控制图片的渲染，确保页面加载时按需显示。  
2. **CSS网格布局**：使用Grid/Flexbox技术实现自适应排版，兼容不同设备。  
3. **分类筛选**：提供分类导航，无刷新切换不同类别的照片。  
4. **过渡动画**：点击分类时，图片通过淡入淡出效果切换，提升用户体验。  

## 未来规划  

1. **图片交互优化**：支持点击放大、左右滑动浏览等增强功能。  
2. **动态数据管理**：使用JSON或本地存储动态加载图片信息。  
3. **动画与特效**：增加CSS动画，提升视觉体验。  
4. **离线访问支持**：结合PWA（渐进式网页应用）技术，实现离线浏览。  

## 部分代码  

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>视界捕手 - 图片展示</title>
  <style>
    /* Reset & Base Styles */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    /* Welcome Screen */
    .welcome-screen {
      position: fixed;
      inset: 0;
      background: linear-gradient(160deg, #f8f9fa 0%, #e2e8f0 50%, #cbd5e0 100%);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 100;
      transition: opacity 0.5s ease;
    }

    .welcome-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2rem;
    }

    .welcome-contacts {
      display: flex;
      gap: 2rem;
      align-items: center;
    }

    .welcome-contacts .contact-link {
      color: #1a365d;
      font-size: 1.1rem;
    }

    .welcome-contacts .contact-link:hover {
      color: #4299e1;
    }

    .welcome-contacts .divider {
      display: block;
      width: 1px;
      height: 24px;
      background-color: rgba(26, 54, 93, 0.2);
    }

    .welcome-title {
      font-size: 4rem;
      font-weight: bold;
      color: #1a365d;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
      animation: fadeInUp 1s ease-out, float 3s ease-in-out infinite;
      letter-spacing: 0.5rem;
      position: relative;
    }

    .welcome-title::after {
      content: '';
      position: absolute;
      bottom: -10px;
      left: 0;
      width: 100%;
      height: 3px;
      background: linear-gradient(90deg, transparent, #4299e1, transparent);
      transform: scaleX(0);
      animation: underline 1.5s ease-out forwards;
    }

    .enter-btn {
      display: inline-block;
      padding: 1rem 2.5rem;
      font-size: 1.2rem;
      color: #1a365d;
      text-decoration: none;
      border: 2px solid #1a365d;
      border-radius: 30px;
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
      background: transparent;
      cursor: pointer;
    }

    .enter-btn::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: #1a365d;
      transform: translateX(-100%);
      transition: transform 0.3s ease;
      z-index: -1;
    }

    .enter-btn:hover {
      color: #fff;
    }

    .enter-btn:hover::before {
      transform: translateX(0);
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background: linear-gradient(160deg, #f8f9fa 0%, #e2e8f0 50%, #cbd5e0 100%);
      color: #1a365d;
      position: relative;
    }

    body::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: 
        linear-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.12) 1px, transparent 1px),
        linear-gradient(45deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
        linear-gradient(-45deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
      background-size: 30px 30px, 30px 30px, 60px 60px, 60px 60px;
      pointer-events: none;
      z-index: 1;
    }

    main, header, footer {
      position: relative;
      z-index: 2;
    }

    /* Header Styles */
    header {
      background-color: #1a365d;
      color: white;
      padding: 1rem;
      text-align: center;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .category-buttons {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 1rem;
    }

    .category-btn {
      padding: 0.625rem 1.5rem;
      border: none;
      border-radius: 9999px;
      background-color: rgba(255, 255, 255, 0.15);
      color: white;
      font-size: 0.9375rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 300ms ease;
    }

    .category-btn:hover {
      background-color: #4299e1;
      transform: scale(1.05);
      box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
    }

    .category-btn.active {
      background-color: #4299e1;
      transform: scale(1.05);
      box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
    }

    /* Main Content Styles */
    main {
      flex-grow: 1;
      padding: 3rem 1rem;
      max-width: 1280px;
      margin: 0 auto;
      width: 100%;
    }

    .image-grid {
      display: grid;
      grid-template-columns: repeat(1, 1fr);
      gap: 1.5rem;
    }

    @media (min-width: 640px) {
      .image-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (min-width: 768px) {
      .image-grid {
        grid-template-columns: repeat(3, 1fr);
      }
    }

    @media (min-width: 1024px) {
      .image-grid {
        grid-template-columns: repeat(4, 1fr);
      }
    }

    .image-card {
      position: relative;
      aspect-ratio: 4/3;
      border-radius: 0.75rem;
      overflow: hidden;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      transition: transform 300ms ease, box-shadow 300ms ease;
      cursor: pointer;
    }

    .image-card:hover {
      transform: scale(1.02);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .image-card img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 500ms ease, filter 300ms ease;
    }

    .image-card:hover img {
      transform: scale(1.05);
      filter: brightness(1.1);
    }

    .image-overlay {
      position: absolute;
      inset: 0;
      background-color: rgba(26, 54, 93, 0.3);
      opacity: 0;
      transition: opacity 300ms ease;
    }

    .image-card:hover .image-overlay {
      opacity: 1;
    }

    .loading-placeholder {
      position: absolute;
      inset: 0;
      background-color: #e2e8f0;
      animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    @keyframes pulse {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: 0.5;
      }
    }

    /* Loading Screen */
    .loading-screen {
      position: fixed;
      inset: 0;
      background-color: #1a365d;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      color: white;
      z-index: 50;
    }

    .loading-spinner {
      width: 48px;
      height: 48px;
      border: 4px solid rgba(255, 255, 255, 0.1);
      border-left-color: #4299e1;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }

    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }



    .contact-link {
      display: flex;
      align-items: center;
      gap: 0.625rem;
      color: white;
      text-decoration: none;
      font-size: 0.95rem;
      transition: color 300ms ease;
    }

    .contact-link:hover {
      color: #4299e1;
    }

    .contact-link svg {
      width: 20px;
      height: 20px;
      transition: transform 300ms ease;
    }

    .contact-link:hover svg {
      transform: scale(1.1);
    }

    .divider {
      display: none;
    }

    @media (min-width: 768px) {
      .divider {
        display: block;
        width: 1px;
        height: 24px;
        background-color: rgba(255, 255, 255, 0.2);
      }
    }
  </style>
</head>
<body>
  <!-- Welcome Screen -->
  <div class="welcome-screen" id="welcomeScreen">
    <div class="welcome-container">
      <h1 class="welcome-title">视界捕手</h1>
      <div class="welcome-contacts">
        <a href="mailto:3785439724@qq.com" class="contact-link">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="20" height="16" x="2" y="4" rx="2"/>
            <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
          </svg>
          <span>3785439724@qq.com</span>
        </a>
        <div class="divider"></div>
        <a href="tel:13105167797" class="contact-link">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
          </svg>
          <span>13105167797</span>
        </a>
      </div>
      <button class="enter-btn" id="enterBtn">点击进入</button>
    </div>
  </div>

  <!-- Loading Screen -->
  <div class="loading-screen" id="loadingScreen">
    <div class="loading-spinner"></div>
    <h2 style="font-size: 1.25rem; font-weight: 500;">加载中...</h2>
  </div>

  <!-- Header -->
  <header>
    <div class="category-buttons" id="categoryButtons">
      <button class="category-btn active" data-category="all">全部</button>
      <button class="category-btn" data-category="people">人物</button>
      <button class="category-btn" data-category="landscape">风景</button>
      <button class="category-btn" data-category="fireworks">烟花</button>
    </div>
  </header>

  <!-- Main Content -->
  <main>
    <div class="image-grid" id="imageGrid"></div>
  </main>



  <script>
    // Image data
    const images = {
      people: [
        '人物/mmexport1742980373362.jpg',
        '人物/mmexport1742980398019.jpg'
      ],
      landscape: [
        '风景/mmexport1742980360458.jpg',
        '风景/mmexport1742980375113.jpg',
        '风景/mmexport1742980376722.jpg',
        '风景/mmexport1742980392015.jpg',
        '风景/mmexport1742980392146.jpg',
        '风景/mmexport1742980395875.jpg',
        '风景/mmexport1742980397065.jpg'
      ],
      fireworks: [
        '烟花/mmexport1742980383662.png',
        '烟花/mmexport1742980385024.jpg'
      ]
    };

    // DOM Elements
    const loadingScreen = document.getElementById('loadingScreen');
    const categoryButtons = document.getElementById('categoryButtons');
    const imageGrid = document.getElementById('imageGrid');
    const loadedImages = new Set();

    // Initialize
    let activeCategory = 'all';

    // Helper function to get filtered images
    function getFilteredImages() {
      if (activeCategory === 'all') {
        return Object.values(images).flat();
      }
      return images[activeCategory] || [];
    }

    // Create image card
    function createImageCard(imageUrl) {
      const card = document.createElement('div');
      card.className = 'image-card';

      const placeholder = document.createElement('div');
      placeholder.className = 'loading-placeholder';
      card.appendChild(placeholder);

      const img = document.createElement('img');
      img.src = `${imageUrl}?auto=format&fit=crop&w=800&q=80`;
      img.alt = 'Gallery image';
      img.style.opacity = '0';
      
      img.onload = () => {
        loadedImages.add(imageUrl);
        placeholder.style.display = 'none';
        img.style.opacity = '1';
      };

      const overlay = document.createElement('div');
      overlay.className = 'image-overlay';

      card.appendChild(img);
      card.appendChild(overlay);

      return card;
    }

    // Render images
    function renderImages() {
      const filteredImages = getFilteredImages();
      imageGrid.innerHTML = '';
      
      filteredImages.forEach(imageUrl => {
        const card = createImageCard(imageUrl);
        imageGrid.appendChild(card);
      });
    }

    // Handle category change
    categoryButtons.addEventListener('click', (e) => {
      if (e.target.classList.contains('category-btn')) {
        const newCategory = e.target.dataset.category;
        
        // Update active button
        document.querySelector('.category-btn.active').classList.remove('active');
        e.target.classList.add('active');
        
        // Update category and render
        activeCategory = newCategory;
        renderImages();
      }
    });

    // Welcome screen handler
    const welcomeScreen = document.getElementById('welcomeScreen');
    const enterBtn = document.getElementById('enterBtn');

    enterBtn.addEventListener('click', () => {
      welcomeScreen.style.opacity = '0';
      setTimeout(() => {
        welcomeScreen.style.display = 'none';
      }, 500);
    });

    // Initial render
    window.addEventListener('load', () => {
      setTimeout(() => {
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
          loadingScreen.style.display = 'none';
        }, 300);
      }, 800);
      
      renderImages();
    });
  </script>
</body>
</html>
```  

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
