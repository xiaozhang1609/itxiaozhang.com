---
title: 用HTML、CSS和JavaScript写一个圣诞氛围的网页
permalink: /create-christmas-themed-webpage-with-html-css-javascript/
date: 2024-12-23 14:04:44
description: 本文介绍了如何使用HTML、CSS和JavaScript创建一个充满圣诞氛围的网页。通过实现雪花飘落、圣诞树和蜡烛闪烁等动态效果。
category:
- 编程案例
tags:
- 编程
- 圣诞
---

> 原文地址：<https://itxiaozhang.com/create-christmas-themed-webpage-with-html-css-javascript/>  
> 本文配合视频食用效果最佳，视频版本在文章末尾。

## 介绍

使用HTML、CSS和JavaScript创建一个充满节日气氛的圣诞节网页，包含雪花飘落、圣诞树、蜡烛闪烁等动画效果。通过这些效果，网页能更好地营造出圣诞节的氛围，并增加互动性。

## 使用

1. 将下面的源码复制到记事本中。
2. 将文件保存为 `.html` 格式（例如 `christmas_scene.html`）。
3. 双击保存的文件，即可在浏览器中打开并查看动感的圣诞节网页。

## 源码

```html
<!--
================================
作者：IT小章
网站：itxiaozhang.com
时间：2024年12月23日
Copyright © 2024 IT小章
================================
-->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Christmas Scene with Candles</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
        }
        .scene {
            background-color: black;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            position: relative;
        }
        #snowCanvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            filter: blur(1px);
        }
        .mainTree {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: min(60vw, 60vh); /* 增大圣诞树尺寸 */
            color: #00ff00;
            z-index: 3;
            transition: all 0.3s ease;
            cursor: pointer;
            animation: sway 4s ease-in-out infinite;
        }
        .mainTree:hover {
            transform: translate(-50%, -50%) scale(1.05);
        }
        @keyframes sway {
            0%, 100% { transform: translate(-50%, -50%) rotate(-1deg); }
            50% { transform: translate(-50%, -50%) rotate(1deg); }
        }
        .candle {
            position: absolute;
            font-size: min(3vw, 3vh);
            color: rgba(255, 255, 224, 0.7);
            text-shadow: 0 0 5px rgba(255, 255, 224, 0.7);
            animation: flicker 2s ease-in-out infinite alternate;
            z-index: 2;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .candle:hover {
            transform: scale(1.2);
            color: rgba(255, 255, 224, 1);
            text-shadow: 0 0 10px rgba(255, 255, 224, 1);
        }
        @keyframes flicker {
            0% { opacity: 0.5; transform: scale(0.95); }
            50% { opacity: 1; transform: scale(1.05); }
            100% { opacity: 0.7; transform: scale(1); }
        }
        @keyframes sparkle {
            0%, 100% { opacity: 0; }
            50% { opacity: 1; }
        }
        .sparkle {
            position: absolute;
            width: 5px;
            height: 5px;
            background-color: white;
            border-radius: 50%;
            animation: sparkle 0.8s linear infinite;
        }
    </style>
</head>
<body>
    <div class="scene">
        <canvas id="snowCanvas"></canvas>
        <div class="mainTree">🎄</div>
    </div>

    <script>
        const scene = document.querySelector('.scene');
        const canvas = document.getElementById('snowCanvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        class Snowflake {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 5 + 2;
                this.speed = Math.random() * 1.5 + 0.5;
                this.opacity = Math.random() * 0.5 + 0.3;
                this.wind = Math.random() * 0.5 - 0.25;
            }

            update() {
                this.y += this.speed;
                this.x += this.wind;
                if (this.y > canvas.height) {
                    this.y = 0;
                    this.x = Math.random() * canvas.width;
                }
                if (this.x > canvas.width) this.x = 0;
                if (this.x < 0) this.x = canvas.width;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
                ctx.fill();
            }
        }

        const snowflakes = Array.from({ length: 150 }, () => new Snowflake());

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            snowflakes.forEach(snowflake => {
                snowflake.update();
                snowflake.draw();
            });
            requestAnimationFrame(animate);
        }
        animate();

        function createCandles() {
            const numCandles = 15;
            const minDistance = 100;
            const candles = [];

            for (let i = 0; i < numCandles; i++) {
                let x, y, overlapping;
                do {
                    x = Math.random() * (window.innerWidth - 100) + 50;
                    y = Math.random() * (window.innerHeight - 100) + 50;
                    overlapping = candles.some(candle => 
                        Math.hypot(candle.x - x, candle.y - y) < minDistance
                    );
                } while (overlapping);

                const candle = document.createElement('div');
                candle.className = 'candle';
                candle.textContent = '🕯️';
                candle.style.left = `${x}px`;
                candle.style.top = `${y}px`;
                const scale = Math.random() * 0.3 + 0.3;
                const rotation = Math.random() * 20 - 10;
                candle.style.transform = `scale(${scale}) rotate(${rotation}deg)`;
                scene.appendChild(candle);
                candles.push({ x, y });
            }
        }

        function handleClick(event) {
            const rect = event.target.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            
            for (let i = 0; i < 10; i++) {
                const sparkle = document.createElement('div');
                sparkle.className = 'sparkle';
                sparkle.style.left = `${x + Math.random() * 40 - 20}px`;
                sparkle.style.top = `${y + Math.random() * 40 - 20}px`;
                sparkle.style.width = `${Math.random() * 3 + 2}px`;
                sparkle.style.height = sparkle.style.width;
                event.target.appendChild(sparkle);
                
                setTimeout(() => sparkle.remove(), 800);
            }
        }

        function adjustLayout() {
            const mainTree = document.querySelector('.mainTree');
            const candles = document.querySelectorAll('.candle');
            
            mainTree.style.fontSize = `min(60vw, 60vh)`; // 增大圣诞树尺寸
            
            candles.forEach(candle => {
                candle.style.fontSize = `min(3vw, 3vh)`;
                const x = Math.random() * (window.innerWidth - 100) + 50;
                const y = Math.random() * (window.innerHeight - 100) + 50;
                candle.style.left = `${x}px`;
                candle.style.top = `${y}px`;
            });
        }

        createCandles();
        adjustLayout();

        document.querySelector('.mainTree').addEventListener('click', handleClick);
        document.querySelectorAll('.candle').forEach(candle => {
            candle.addEventListener('click', handleClick);
        });
        window.addEventListener('resize', adjustLayout);
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
