# fix_frames.py
import os
import sys
from PySide6.QtGui import QImage, QColor
from PySide6.QtCore import QCoreApplication, QPoint

def flood_fill_background(image):
    """
    Yeh function image ke chaaron corners se background detection shuru karega (Flood Fill).
    Isse background ka transparent/grey area detect hoga, lekin character ke andar 
    ka white color (water bottle, heels, eyes) puri tarah safe rahega!
    """
    width = image.width()
    height = image.height()
    
    # Track visited pixels
    visited = [[False for _ in range(height)] for _ in range(width)]
    
    # Hum targets dhoondhenge jo pure white ya checkered background patterns hain
    def is_background_pixel(x, y):
        color = QColor(image.pixel(x, y))
        r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
        
        # Background checking conditions:
        # 1. Pure or near-white (r, g, b > 210)
        # 2. Checkered grey pixels
        # 3. Already transparent pixels (a == 0)
        if a == 0:
            return True
        if r > 210 and g > 210 and b > 210:
            return True
        if r == g == b and 100 < r < 240:
            return True
        return False

    # Seed points starting from all 4 corners and edges
    queue = []
    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(1, height - 1):
        queue.append((0, y))
        queue.append((width - 1, y))

    # Flood fill queue processing
    background_mask = [[False for _ in range(height)] for _ in range(width)]
    
    while queue:
        cx, cy = queue.pop(0)
        if cx < 0 or cx >= width or cy < 0 or cy >= height:
            continue
        if visited[cx][cy]:
            continue
            
        visited[cx][cy] = True
        
        if is_background_pixel(cx, cy):
            background_mask[cx][cy] = True
            # Check 4 neighboring pixels
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height and not visited[nx][ny]:
                    queue.append((nx, ny))

    # Final step: Apply background colors based on smart mask
    for y in range(height):
        for x in range(width):
            if background_mask[x][y]:
                # Background ko smooth transparent black shady look dena
                image.setPixelColor(x, y, QColor(15, 15, 20, 190))
            # Agar mask background me nahi hai, toh original pixel safe rahega (bottle/heels unchanged!)
                
    return image

def convert_frames_background():
    app = QCoreApplication(sys.argv)
    frames_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames")
    
    if not os.path.exists(frames_dir):
        print("[-] 'frames' folder not found!")
        return

    files = sorted([f for f in os.listdir(frames_dir) if f.lower().endswith('.png')])
    print(f"[+] Total {len(files)} frames mile. Smart background conversion process shuru...")

    for file_name in files:
        file_path = os.path.join(frames_dir, file_name)
        image = QImage(file_path).convertToFormat(QImage.Format_ARGB32)
        
        # Apply smart flood fill background cleaner
        processed_image = flood_fill_background(image)
        processed_image.save(file_path)
        print(f"[✔] Smart Cleaned: {file_name}")

    print("[+] all frames flawlessly up-to-date and cleaned !")

if __name__ == "__main__":
    convert_frames_background()