@echo off
echo [1/3] Cleaning and Generating static files...
call hexo clean
call hexo g

echo [2/3] Adding changes to Git...
git add .

echo [3/3] Committing and Pushing to GitHub...
git commit -m "Deploy Update: %date% %time%"
git push origin main

echo.
echo [SUCCESS] Blog deployed successfully!
pause
