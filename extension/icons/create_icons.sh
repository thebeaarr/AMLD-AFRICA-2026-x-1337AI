#!/bin/bash
# Create simple placeholder icons using ImageMagick (if available)
# Otherwise, download from a placeholder service

if command -v convert &> /dev/null; then
  # Create icons with ImageMagick
  convert -size 16x16 xc:none -fill "#667eea" -draw "circle 8,8 8,2" icon16.png
  convert -size 48x48 xc:none -fill "#667eea" -draw "circle 24,24 24,4" icon48.png
  convert -size 128x128 xc:none -fill "#667eea" -draw "circle 64,64 64,10" icon128.png
  echo "Icons created with ImageMagick"
else
  # Download placeholder icons
  curl -s "https://via.placeholder.com/16/667eea/ffffff?text=AI" -o icon16.png
  curl -s "https://via.placeholder.com/48/667eea/ffffff?text=AI" -o icon48.png
  curl -s "https://via.placeholder.com/128/667eea/ffffff?text=AI" -o icon128.png
  echo "Icons downloaded"
fi
